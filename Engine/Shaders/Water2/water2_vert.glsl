#version 140
in vec2 vtx_texcoord0;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;
uniform float offset;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
uniform mat4 gl_TextureMatrix[]; // gl_TextureMatrix[0]
uniform mat3 tpose_view_to_model;
uniform mat4 trans_model_to_view; // gsg.getExternalTransform()

out vec4 position;
out vec4 l_texcoord0; // l_texcoord0
out vec4 l_texcoord1; // l_texcoord1
out vec4 l_texCoordReflec; // l_texCoordReflec
out vec4 l_eye_normal; // l_eye_normal
out vec4 l_eye_position; // l_eye_position

void main()
{
    vec4 l_worldPos = p3d_ModelMatrix * p3d_Vertex;
    position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    l_texcoord0.xy = vtx_texcoord0 * 20.0 + offset * 0.01;
    l_texcoord1.xy = vtx_texcoord0 * 20.0 - offset * 0.01;
    l_texCoordReflec = gl_TextureMatrix[0] * l_worldPos;
    l_eye_normal.xyz = tpose_view_to_model * p3d_Normal.xyz;
    l_eye_normal.w = 0;
    l_eye_position = trans_model_to_view * position;
}
