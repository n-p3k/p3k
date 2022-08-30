
from pyrr import Matrix44
import moderngl
import moderngl_window as mglw
from moderngl_window import geometry

class Cube:
    def __init__(self, ctx):
        self.ctx = ctx 

    def init(self):
        shader_source = {
            'vertex_shader': '''
                #version 330

                in vec3 in_position;
                in vec3 in_normal;

                uniform vec3 pos_offset;

                uniform Projection {
                    uniform mat4 matrix;
                } proj;

                uniform View {
                    uniform mat4 matrix;
                } view;

                out vec3 normal;
                out vec3 pos;

                void main() {
                    vec4 p = view.matrix * vec4(in_position + pos_offset, 1.0);
                    gl_Position =  proj.matrix * p;
                    mat3 m_normal = transpose(inverse(mat3(view.matrix)));
                    normal = m_normal * in_normal;
                    pos = p.xyz;
                }
            ''',
            'fragment_shader': '''
                #version 330

                out vec4 color;

                in vec3 normal;
                in vec3 pos;

                void main() {
                    float l = dot(normalize(-pos), normalize(normal));
                    color = vec4(1.0) * (0.25 + abs(l) * 0.75);
                }
            ''',
        }
        self.cube = geometry.cube(size=(10,10,10))
        self.vol_prog = self.ctx.program(**shader_source)
        self.vol_prog['pos_offset'].value = (1.1, 0, 0)
        self.vol_vao = self.cube.instance(self.vol_prog)

        self.m_proj = Matrix44.perspective_projection(
            85, .0833,  # fov, aspect
            0.1, 250.0,  # near, far
            dtype='f4',
        )

        proj_uniform1 = self.vol_prog['Projection']
        view_uniform1 = self.vol_prog['View']

        self.proj_buffer = self.ctx.buffer(reserve=proj_uniform1.size)
        self.view_buffer = self.ctx.buffer(reserve=view_uniform1.size)

        proj_uniform1.binding = 1
        view_uniform1.binding = 2

        self.proj_buffer.write(self.m_proj.tobytes())

        self.scope1 = self.ctx.scope(
            self.ctx.fbo,
            enable_only=moderngl.CULL_FACE | moderngl.DEPTH_TEST,
            uniform_buffers=[
                (self.proj_buffer, 1),
                (self.view_buffer, 2),
            ],
        )
        self.z = -5.0


    def render(self, t):
        rotation = Matrix44.from_eulers((t,t,t), dtype='f4')
        self.z += 0.01
        translation = Matrix44.from_translation((0.0, 0.0, self.z), dtype='f4')
        modelview = translation * rotation
        self.view_buffer.write(modelview)
        with self.scope1:
            self.vol_vao.render(mode=moderngl.TRIANGLES)

        #self.cube.render(self.vol_prog)



