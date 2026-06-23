import ctypes
from concurrent.futures import ProcessPoolExecutor
from typing import TYPE_CHECKING, Any, TypeAlias, cast

import cv2 as cv
import glfw
import numpy as np
from OpenGL import GL
from urenderer.geometry.mesh import Mesh
from urenderer.node import Camera, Node
from urenderer.renderer.renderer import Renderer
from urenderer.utils import get_filename_unique

from .material import Material

if TYPE_CHECKING:
    GLFWWindow = Any
else:
    GLFWWindow = ctypes.POINTER(glfw._GLFWwindow)


def save_frame(path: str, frame: np.ndarray) -> None:
    '''
    Save a frame

    Args:
        path (str): path to save
        frame (np.ndarray): frame
    '''
    cv.imwrite(path, frame)


class OpenGLRenderer(Renderer):
    '''
    Renderer using OpenGL
    '''

    def __init__(self, screen_width: int, screen_height: int) -> None:
        '''
        OpenGLRenderer initializer.

        Args:
            screen_width (int): screen width
            screen_height (int): screen height
            show (bool, optional): if should show the rendered frame. Defaults to True.
        '''
        super().__init__(screen_width, screen_height)
        self._executor = ProcessPoolExecutor(max_workers=1)

        glfw.init()
        window = glfw.create_window(screen_width, screen_height, "OpenGL Renderer", None, None)
        glfw.make_context_current(window)

        GL.glViewport(0, 0, screen_width, screen_height)
        # Inicializa o GLFW, core profile e OpenGL 3.3
        # Cria a janela, associando ela ao contexto
        # e configurando o tamanho dela no OpenGl

        #########################################################################

        glfw.set_framebuffer_size_callback(
            window, self._framebuffer_size_callback)

        GL.glEnable(GL.GL_DEPTH_TEST)

        self._window = cast(GLFWWindow, window)
        self.background_color = np.array([1.0, 0.0, 1.0, 1.0])

    def _framebuffer_size_callback(self, window: GLFWWindow,
                                   width: int, height: int):
        '''
        Callback for a change in the framebuffer size

        Args:
            window (GLFWWindow): window with size change
            width (int): new width
            height (int): new heigth
        '''
        GL.glViewport(0, 0, width, height)

    def start(self, camera: Camera, view_matrix: np.ndarray, name: str) -> None:
        '''
        Start the frame rendering

        Args:
            camera (Camera): current camera.
            view_matrix (np.ndarray): camera view matrix.
            name (str): name of the application
        '''
        self._view_matrix = view_matrix
        self._projection_matrix = camera.projection_matrix
        self._name = name

        glfw.set_window_title(self._window, name)

        while not glfw.window_should_close(self._window):
            GL.glClearColor(*self.background_color)
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        # Limpe os buffers de cor e profundidade (COLOR_BUFFER e DEPTH_BUFFER)
        # Para o de cor, utilize a cor self.background_color

        #########################################################################

    def validate(self, node: Node) -> bool:
        '''
        Validate a node for rendering.

        Check if the node is compatible to be rendered with this renderer.

        Args:
            node (Node): node to validate.

        Returns:
            bool: True if the node is valid
        '''
        return ("material" in node.render_data and
                "mesh" in node.render_data)

    def render_valid_node(self, node: Node, model_transformation: np.ndarray):
        '''
        Renders a validated node

        Args:
            node (Node): node to render
            model_transformation (np.ndarray): node model transformation in the scene
        '''

        material: Material = node.render_data["material"]
        mesh: Mesh = node.render_data["mesh"]

        material.use()

        material.shader.set_uniform("modelTransformation", model_transformation.astype(np.float32))
        material.shader.set_uniform("viewTransformation", self._view_matrix.astype(np.float32))
        material.shader.set_uniform("projectionMatrix", self._projection_matrix.astype(np.float32)) 

        # Defina as uniforms 'modelTransformation', 'viewTransformation' e
        # 'projectionMatrix' do material.shader, as matrizes de transformação de
        # coordenadas 4x4.
        #
        # Utilize o método set_uniform do shader, pois não queremos alterar a
        # uniform para todo uso do material.
        #
        # Atente-se que os valores precisam ser convertidos para np.float32

        #########################################################################

        mesh.draw()

    def end(self, capture: bool = False):
        '''
        Ends the frame rendering

        Args:
            capture (bool, optional): if should save the current frame. Defaults to False.
        '''

        if capture:
            GL.glPixelStorei(GL.GL_PACK_ALIGNMENT, 1)

            frame_data = GL.glReadPixels(0,  # first pixel x
                                         0,  # first pixel y
                                         self.screen_width,  # dimensão do retângulo sendo lido
                                         self.screen_height,  # dimensão do retângulo sendo lido
                                         GL.GL_BGRA,
                                         GL.GL_UNSIGNED_BYTE)
            frame_data = cast(bytes, frame_data)

            frame = np.frombuffer(frame_data, np.uint8)
            frame = frame.reshape([self.screen_height, self.screen_width, 4])
            frame = np.flipud(frame)

            filename = get_filename_unique(self._name)

            self._executor.submit(save_frame, filename, frame)

        glfw.swap_buffers(self._window)
        # Troque o buffer frontal e traseiro, mostrando o novo buffer renderizado

        #########################################################################

        glfw.poll_events()

    def should_stop(self) -> bool:
        return glfw.window_should_close(self._window)

    def __del__(self):
        self._executor.shutdown()
        glfw.terminate()
