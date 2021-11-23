#version 140

struct p3d_LightSourceParameters {
  vec4 color;
  vec3 spotDirection;
  sampler2DShadow shadowMap;
  mat4 shadowViewMatrix;
};

uniform p3d_LightSourceParameters my_light;
uniform sampler2D p3d_Texture0;
uniform vec3 camera_pos;
uniform float shadow_blur;

in vec2 uv;
in vec4 shadow_uv;
in vec3 normal;
in vec3 ambient_color;

out vec4 color;

float textureProjSoft(sampler2DShadow tex, vec4 uv, float bias, float blur)
    {
    float result = textureProj(tex, uv, bias);
    result += textureProj(tex, vec4(uv.xy + vec2( -0.326212, -0.405805)*blur, uv.z-bias, uv.w));
    result += textureProj(tex, vec4(uv.xy + vec2(-0.840144, -0.073580)*blur, uv.z-bias, uv.w));
    result += textureProj(tex, vec4(uv.xy + vec2(-0.695914, 0.457137)*blur, uv.z-bias, uv.w));
    result += textureProj(tex, vec4(uv.xy + vec2(-0.203345, 0.620716)*blur, uv.z-bias, uv.w));
    result += textureProj(tex, vec4(uv.xy + vec2(0.962340, -0.194983)*blur, uv.z-bias, uv.w));
    result += textureProj(tex, vec4(uv.xy + vec2(0.473434, -0.480026)*blur, uv.z-bias, uv.w));
    result += textureProj(tex, vec4(uv.xy + vec2(0.519456, 0.767022)*blur, uv.z-bias, uv.w));
    result += textureProj(tex, vec4(uv.xy + vec2(0.185461, -0.893124)*blur, uv.z-bias, uv.w));
    result += textureProj(tex, vec4(uv.xy + vec2(0.507431, 0.064425)*blur, uv.z-bias, uv.w));
    result += textureProj(tex, vec4(uv.xy + vec2(0.896420, 0.412458)*blur, uv.z-bias, uv.w));
    result += textureProj(tex, vec4(uv.xy + vec2(-0.321940, -0.932615)*blur, uv.z-bias, uv.w));
    result += textureProj(tex, vec4(uv.xy + vec2(-0.791559, -0.597705)*blur, uv.z-bias, uv.w));
    return result/13.0;
    }

void main()
    {
    //texture
    vec4 tex = texture(p3d_Texture0, uv);
    //light ..sort of, not important
    vec3 light = my_light.color.rgb*max(dot(normalize(normal),-my_light.spotDirection), 0.0);

    //shadows
    float shadow = textureProjSoft(my_light.shadowMap, shadow_uv, 0.0001, shadow_blur);

    //make the shadow brighter
    shadow=0.5+shadow*0.5;

    color=vec4(tex.rgb*(light*shadow+ambient_color), tex.a);

    }