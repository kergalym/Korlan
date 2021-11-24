#version 150

#define MAX_LIGHTS 4

uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ProjectionMatrix;
uniform mat3 p3d_NormalMatrix;

uniform struct p3d_LightSourceParameters {
    vec4 color;
    vec4 ambient;
    vec4 diffuse;
    vec4 specular;
    vec4 position;
    vec3  spotDirection;
    float spotExponent;
    float spotCutoff;
    float spotCosCutoff;
    float constantAttenuation;
    float linearAttenuation;
    float quadraticAttenuation;
    vec3 attenuation;
    sampler2DShadow shadowMap;
    mat4 shadowViewMatrix;
  } p3d_LightSource[MAX_LIGHTS];


uniform mat4 p3d_ProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;
uniform mat4 p3d_TextureMatrix;

attribute vec4 p3d_Vertex;
attribute vec4 p3d_Color;
attribute vec3 p3d_Normal;
attribute vec4 p3d_Tangent;
attribute vec2 p3d_MultiTexCoord0;

varying vec3 vtx_position;
varying vec4 vtx_color;
varying mat3 vtx_tbn;
varying vec2 vtx_texcoord;

varying vec4 vtx_shadow_position[MAX_LIGHTS];

void main() {
    // Calculate vertex position
    vec4 vtx_pos4 = p3d_ModelViewMatrix * p3d_Vertex;
    vtx_position = vec3(vert_pos4);
    vtx_color = p3d_Color;
    // calculate normal and texture coordinates
    vec3 normal = normalize(p3d_NormalMatrix * p3d_Normal);
    vtx_texcoord = (p3d_TextureMatrix * vec4(p3d_MultiTexCoord0, 0, 1)).xy;
    // Calculate light for light sources
    for (int i = 0; i < p3d_LightSource.length(); ++i) {
        vtx_shadow_pos[i] = p3d_LightSource[i].shadowViewMatrix * vtx_pos4;
    }
    // Tangent Bitangent and Normal calculations
    vec3 tangent = normalize(vec3(p3d_ModelViewMatrix * vec4(p3d_Tangent.xyz, 0.0)));
    vec3 bitangent = cross(normal, tangent) * p3d_Tangent.w;
    vtx_tbn = mat3(
        tangent,
        bitangent,
        normal
    );
    // Calculate vertex position in clipping space
    gl_Position = p3d_ProjectionMatrix * vtx_pos4;
}