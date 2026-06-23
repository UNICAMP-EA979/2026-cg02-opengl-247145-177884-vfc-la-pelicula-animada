from typing import Any, cast

import numpy as np
from OpenGL import GL


def check_shader_compilation(shader: int, name: str = "") -> None:
    '''
    Checks for shader compilation errors

    Args:
        shader (int): shader to check
        name (str, optional): Name of the shader for exception. Defaults to "".

    Raises:
        RuntimeError: if there is a compilation error
    '''
    success = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
    if not success:
        info_log = GL.glGetShaderInfoLog(shader)
        raise RuntimeError(f"Shader Compilation Failed - {name}\n\n" +
                           info_log.decode("utf-8"))


def check_program_linking(shader_program: int) -> None:
    '''
    Checks for program compilation error

    Args:
        shader_program (int): program to check

    Raises:
        RuntimeError: if there is a linking error
    '''
    success = GL.glGetProgramiv(shader_program, GL.GL_LINK_STATUS)
    if not success:
        info_log = GL.glGetProgramInfoLog(shader_program)
        raise RuntimeError("Program Linking Failed\n\n" +
                           info_log.decode("utf-8"))


class Shader:
    '''
    Stores an OpenGL shader program
    '''

    _program_cache: dict[str, Any] = {}

    def __init__(self, vertex_path: str, fragment_path: str) -> None:
        '''
        Shader constructor

        Args:
            vertex_path (str): path of the vertex shader file.
            fragment_path (str): path of the fragment shader file
        '''

        # Lê os arquivos
        with open(vertex_path, "r") as file:
            vertex_shader_source = file.read()
        with open(fragment_path, "r") as file:
            fragment_shader_source = file.read()

        # Checa se o programa já foi compilado e linkado
        full_source = vertex_shader_source+fragment_shader_source
        if full_source not in Shader._program_cache:
            # Compila o programa ainda não cacheado
            # Cria e compila o vertex shader
            vertex_shader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
            GL.glShaderSource(vertex_shader, vertex_shader_source)
            GL.glCompileShader(vertex_shader)
            #########################################################################

            vertex_shader = cast(int, vertex_shader)
            check_shader_compilation(vertex_shader, "VERTEX")

            # Cria e compila o fragment shader
            fragment_shader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
            GL.glShaderSource(fragment_shader, fragment_shader_source)
            GL.glCompileShader(fragment_shader)
            #########################################################################

            fragment_shader = cast(int, fragment_shader)
            check_shader_compilation(fragment_shader, "FRAGMENT")

            # Cria e linka o programa
            shader_program = GL.glCreateProgram()
            GL.glAttachShader(shader_program, vertex_shader)
            GL.glAttachShader(shader_program, fragment_shader)
            GL.glLinkProgram(shader_program)
            #########################################################################

            shader_program = cast(int, shader_program)
            check_program_linking(shader_program)

            GL.glDeleteShader(vertex_shader)
            GL.glDeleteShader(fragment_shader)

            Shader._program_cache[full_source] = shader_program

        self.shader_program = Shader._program_cache[full_source]
        self.uniform_location: dict[str, int] = {}

    def use(self) -> None:
        '''
        Use the shader, activating it in the current rendering state
        '''
        GL.glUseProgram(self.shader_program)
  
        # Usa o programa compilado e linkado anteriormente no contexto atual

        #########################################################################

    def _get_uniform_location(self, name: str) -> int:
        '''
        Get to location of a uniform

        Args:
            name (str): name of the uniform

        Returns:
            int: uniform location
        '''

        # Cacheia o local da uniform para melhor performance
        if name not in self.uniform_location:
            self.uniform_location[name] = GL.glGetUniformLocation(
                self.shader_program, name)

        return self.uniform_location[name]

    def set_uniform(self, name: str, value: bool | int | float | np.ndarray) -> None:
        '''
        Set the value of a uniform

        Args:
            name (str): name of the uniform
            value (bool | int | float | np.ndarray): value to set

        Raises:
            ValueError: if the value type is not supported
        '''
        location = self._get_uniform_location(name)


        # Defina o valor corretamente da uniforme para cada tipo
        # https://registry.khronos.org/OpenGL-Refpages/gl4/html/glUniform.xhtml

        if isinstance(value, bool):
            GL.glUniform1i(location, int(value))
        elif isinstance(value, int):
            GL.glUniform1i(location, value)
        elif isinstance(value, float):
            GL.glUniform1f(location, value)
        elif isinstance(value, np.ndarray):
            if value.dtype == np.float32 and value.shape == (4, 4):
                GL.glUniformMatrix4fv(location, 1, GL.GL_FALSE, value)
            else:
                raise ValueError(f"Value type {type(value)} not supported")
        else:
            raise ValueError(f"Value type {type(value)} not supported")

        #########################################################################
