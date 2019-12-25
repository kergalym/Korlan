#version 140

struct p3d_LightSourceParameters {
  vec4 color;
  vec3 spotDirection;
  sampler2DShadow shadowMap;
  mat4 shadowMatrix;
};

uniform p3d_LightSourceParameters my_light;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat3 p3d_NormalMatrix;

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;

out vec2 uv;
out vec4 shadow_uv;
out vec3 normal;

void main()
    {
    //position
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    //normal
    normal = p3d_NormalMatrix * p3d_Normal;
    //uv
    uv = p3d_MultiTexCoord0;
    //shadows
    shadow_uv = my_light.shadowMatrix * p3d_Vertex;
    }