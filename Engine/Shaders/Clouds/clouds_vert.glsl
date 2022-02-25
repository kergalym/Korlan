#version 130

uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec4 p3d_MultiTexCoord0;
in vec4 offset;
in vec4 uv;
in vec4 p3d_Color;

out vec4 texcoord0;
out vec4 texcoord1;
out vec4 position;
out vec4 color;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    position = gl_Position;
    texcoord0 = p3d_MultiTexCoord0+offset+vec4(uv.xy, 0.0, 0.0);
    texcoord1 = p3d_MultiTexCoord0+offset+vec4(uv.zw, 0.0, 0.0);
    color = p3d_Color;
}
