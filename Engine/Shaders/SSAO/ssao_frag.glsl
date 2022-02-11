#version 130

// Fragment inputs
in vec4 position;
in vec2 texcoord;
in vec2 g_screen_size;

uniform sampler2D normal_map;
uniform sampler2D rnd_normal_map;
uniform sampler2D depth_map;

uniform vec4 texpad_depth;
uniform vec4 vs_cam_pos; // position of camera in view space
uniform vec4 vs_model_pos; // position of model in view space

//uniform mat4 trans_world_to_view; // test!
//uniform mat4 trans_clip_to_view; // test!

out vec4 o_color;

float g_sample_rad = 1;
float g_intensity = 0.5;
float g_scale = 1;
float g_bias = 0.01;
float random_size = 64;

vec4 samples[8] = vec4[8](
    vec4(0.355512,    -0.709318,  -0.102371,  0.0 ),
    vec4(0.534186,    0.71511,    -0.115167,  0.0 ),
    vec4(-0.87866,    0.157139,   -0.115167,  0.0 ),
    vec4(0.140679,    -0.475516,  -0.0639818, 0.0 ),
    vec4(-0.0796121,  0.158842,   -0.677075,  0.0 ),
    vec4(-0.0759516,  -0.101676,  -0.483625,  0.0 ),
    vec4(0.12493,     -0.0223423, -0.483625,  0.0 ),
    vec4(-0.0720074,  0.243395,   -0.967251,  0.0 )

);

float doAmbientOcclusion(in vec2 tcoord,in vec2 uv, in vec3 p, in vec3 cnorm, in sampler2D depth)
{
    vec3 diff = texture2D(depth,uv+tcoord).xyz - p;
    vec3 v = normalize(diff);
    float d = length(diff)*g_scale;
    return max(0.0,dot(cnorm,v)-g_bias)*(1.0/(1.0+d))*g_intensity;
}

void main() {
    // calculate fragment position in clip space
    vec4 c_position;
    c_position.xy = position.xy / position.w;

    // textures input
    vec2 texcoords = vec2(c_position.xy) * texpad_depth.xy + texpad_depth.xy;
    vec3 normal = texture2D(normal_map, texcoords).rgb;
    float depth = texture2D(depth_map, texcoords).a;
    vec2 random = normalize(texture2D(rnd_normal_map, g_screen_size * texcoords / random_size).xy * 2.0f - 1.0f);

    // calculate point illuminated
    vec4 P;
    P.xy = c_position.xy;
    P.z = depth;
    P.w = 1;
    //P = mul(trans_clip_to_view, P); // test!
    P /= P.w*2;

    // calculate normal
    vec3 N;
    N = normal;
    N.xyz = 2 * N.xyz;
    N.xyz = N.xyz - 1;
    // N = mul(mat3(trans_world_to_view),N); // test!
        
    // calculate light vector
    vec3 L = (vs_model_pos - P).xyz;
    //if(k_dirlight.x == 1) L = (vspos_light - vspos_origin);

    // calculate ray length
    float len = length(L);
    
    L = normalize(L);
    N = normalize(N);
    vec3 V,H;
       
    V = normalize(vs_cam_pos - P).xyz;

    const vec2 vec[4] =  vec2[4](vec2(1,0),vec2(-1,0),
                        vec2(0,1),vec2(0,-1));

    vec3 p = P.xyz;
    vec3 n = N;
    vec2 rand = random;

    float ao = 0.0f;
    float rad = g_sample_rad/p.z;

    // SSAO Calculation
    int iterations = 4;
    for (int j = 0; j < iterations; ++j)
    {
      vec2 coord1 = reflect(vec[j],rand)*rad;
      vec2 coord2 = vec2(coord1.x*0.707 - coord1.y*0.707,
                              coord1.x*0.707 + coord1.y*0.707);
      
      ao += doAmbientOcclusion(texcoords,coord1*0.25, p, n,depth_map);
      ao += doAmbientOcclusion(texcoords,coord2*0.5, p, n,depth_map);
      ao += doAmbientOcclusion(texcoords,coord1*0.75, p, n,depth_map);
      ao += doAmbientOcclusion(texcoords,coord2, p, n,depth_map);
    }
    ao /= iterations * 4.0;
    o_color.xyz = P.xyz;
}
