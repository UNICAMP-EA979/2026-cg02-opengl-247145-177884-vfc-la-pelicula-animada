from ctypes import c_void_p

import glfw
import numpy as np
from OpenGL import GL

# Inicializa o GLFW
glfw.init()

# Força versões do OpenGL
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
# Usa apenas Core profile
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

# Cria janela
window = glfw.create_window(800, 600, "LearnOpenGL", None, None)
glfw.make_context_current(window)

# Seta tamamho da tela
GL.glViewport(0, 0, 800, 600)


# Redimensiona a tela quando o usuário altera o tamanho


def framebuffer_size_callback(window, width, height):
    GL.glViewport(0, 0, width, height)


glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

# Cria o Vertex shader
vertex_shader_source = GL.glCreateShader(GL.GL_VERTEX_SHADER) 
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec2 uv;

out vec3 color;

void main()
{
   gl_Position = vec4(position.x, position.y, position.z, 1.0);
   color = vec3(uv, 0.0);
}


vertex_shader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
GL.glShaderSource(vertex_shader, vertex_shader_source)
GL.glCompileShader(vertex_shader)

# Cria o fragment shader
fragment_shader_source = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
#version 330 core
in vec3 color;

out vec4 FragColor;

void main()
{
    FragColor = vec4(color, 1.0f);
} 


fragment_shader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
GL.glShaderSource(fragment_shader, fragment_shader_source)
GL.glCompileShader(fragment_shader)

# Cria o programa
shader_program = GL.glCreateProgram()
GL.glAttachShader(shader_program, vertex_shader)
GL.glAttachShader(shader_program, fragment_shader)
GL.glLinkProgram(shader_program)

GL.glDeleteShader(vertex_shader)
GL.glDeleteShader(fragment_shader)

# Dados para renderizar um quadrado
# [x, y, z, u, v]
data = np.array([
    0.5,  0.5, 0.0, 0.0, 0.0,  # top right
    0.5, -0.5, 0.0, 0.0, 1.0,  # bottom right
    -0.5, -0.5, 0.0, 1.0, 1.0,  # bottom left
    -0.5,  0.5, 0.0, 1.0, 0.0  # top left
], dtype=np.float32)

indices = np.array([0, 1, 3,
                    1, 2, 3], dtype=np.uint32)

# Cria os buffers para renderizar o quadrado utilizando os dados
vao = GL.glGenVertexArrays(1)
vbo = GL.glGenBuffers(1)
ebo = GL.glGenBuffers(1)

GL.glBindVertexArray(vao)

GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
GL.glBufferData(GL.GL_ARRAY_BUFFER, data.nbytes,
                data, GL.GL_STATIC_DRAW)

GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, ebo)
GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER,
                indices.nbytes, indices, GL.GL_STATIC_DRAW)

float_size = np.dtype(np.float32).itemsize

GL.glVertexAttribPointer(0, 3,
                         GL.GL_FLOAT, GL.GL_FALSE,
                         5*float_size,
                         c_void_p(0))
GL.glEnableVertexAttribArray(0)

GL.glVertexAttribPointer(1, 2,
                         GL.GL_FLOAT, GL.GL_FALSE,
                         5*float_size,
                         c_void_p(3*float_size))
GL.glEnableVertexAttribArray(1)

GL.glBindVertexArray(0)


# Loop de renderização
while not glfw.window_should_close(window):

    # Limpa os buffers
    GL.glClearColor(1.0, 0.0, 1.0, 1.0)
    GL.glClear(int(GL.GL_COLOR_BUFFER_BIT) | int(GL.GL_DEPTH_BUFFER_BIT))

    # Desenha o quadrado
    GL.glUseProgram(shader_program)
    GL.glBindVertexArray(vao)
    GL.glDrawElements(GL.GL_TRIANGLES, 6, GL.GL_UNSIGNED_INT, None)

    # Pega o buffer sendo renderizado e coloca na tela
    glfw.swap_buffers(window)

    glfw.poll_events()  # Checa eventos (inputs)

# Finaliza o glfw
glfw.terminate()
