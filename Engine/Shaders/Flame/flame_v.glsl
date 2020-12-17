#version 120

uniform mat4 p3d_ModelViewProjectionMatrix;
varying vec2 uv;

void mainVertex(in vec4 p3d_Vertex)
{
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    uv=gl_Position.xy*0.5+0.5;
}