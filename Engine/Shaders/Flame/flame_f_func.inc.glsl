#define ITERATIONS 15
#define SPEED 15.0
#define DISPLACEMENT 0.03
#define TIGHTNESS 10.0
#define YOFFSET 0.1
#define YSCALE 0.25
#define FLAMETONE vec3(60.0, 5.0, 2.0)

float shape(in vec2 pos) // a blob shape to distort
{
	return clamp( sin(pos.x*3.1416) - pos.y+YOFFSET, 0.0, 1.0 );
}

float iqnoise( in vec3 x, in sampler2D p3d_Texture0 ) // iq noise function
{
	vec3 p = floor(x);
    vec3 f = fract(x);
	f = f*f*(3.0-2.0*f);
	vec2 uv = (p.xy+vec2(37.0,17.0)*p.z) + f.xy;
	vec2 rg = textureLod(p3d_Texture0, (uv+ 0.5)/256.0, 0.0 ).yx;
	return mix( rg.x, rg.y, f.z ) * 2.0 - 1.0;
}

float noise(vec3 p)
{
	vec3 i = floor(p);
	vec4 a = dot(i, vec3(1., 57., 21.)) + vec4(0., 57., 21., 78.);
	vec3 f = cos((p-i)*acos(-1.))*(-.5)+.5;
	a = mix(sin(cos(a)*a),sin(cos(1.+a)*(1.+a)), f.x);
	a.xy = mix(a.xz, a.yw, f.y);
	return mix(a.x, a.y, f.z);
}