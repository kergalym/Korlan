#version 130

// Volcano - Dave Hoskins. 2013.
// https://www.shadertoy.com/view/4dfGW4
// V. 1.2 Rocks.
// V. 1.1 Removed texture dependancy and increased detail at base.

uniform sampler2D p3d_Texture0;
uniform float iTime;
out vec4 p3d_FragColor;
in vec2 texcoord;

float hash( float n )
{
    return fract(sin(n)*43758.5453);
}

float noise( in vec2 x )
{
    vec2 p = floor(x);
    vec2 f = fract(x);

    f = f*f*(3.0-2.0*f);

    float n = p.x + p.y*57.0;

    float res = mix(mix( hash(n+  0.0), hash(n+  1.0),f.x),
                    mix( hash(n+ 57.0), hash(n+ 58.0),f.x),f.y);

    return res;
}

float SmokeParticle(vec2 loc, vec2 pos, float size, float rnd)
{
	loc = loc-pos;
	float d = dot(loc, loc)/size;
	// Outside the circle? No influence...
	if (d > 1.0) return 0.0;

	// Rotate the particles...
	float r= time*rnd*1.85;
	float si = sin(r);
	float co = cos(r);
	// Grab the rotated noise decreasing resolution due to Y position.
	// Also used 'rnd' as an additional noise changer.
	d = noise(hash(rnd*828.0)*83.1+mat2(co, si, -si, co)*loc.xy*2./(pos.y*.16)) * pow((1.-d), 3.)*.7;
	return d;
}

float RockParticle(vec2 loc, vec2 pos, float size, float rnd)
{
	loc = loc-pos;
	float d = dot(loc, loc)/size;
	// Outside the circle? No influence...
	if (d > 1.0) return 0.0;
	float r= time*1.5 * (rnd);
	float si = sin(r);
	float co = cos(r);
	d = noise((rnd*38.0)*83.1+mat2(co, si, -si, co)*loc*143.0) * pow(1.0-d, 15.25);
	return pow(d, 2.)*5.;

}

void main()
{
      time = (iTime+1.);

      vec2 uv = texcoord.xy;
      uv.x *= texcoord.x/texcoord.y;
      vec3 col = mix(vec3(.95, 1., 1.0), vec3(.75, .89, 1.0), uv.y+.75);

      // Position...
      uv = uv + vec2(0.1,1.1);
      // Loop through rock particles...
      for (float i = 0.0; i < 40.0; i+=1.0)
      {
      	float t = time*1.3+i*(2.+hash(i*-1239.)*2.0);
      	float sm = mod(t, 9.3)*.8;
      	float rnd = floor(t / 9.3);
      	vec2 pos = vec2(0.0, sm) *.5;
      	pos.x += (hash(i*33.0+rnd)-.5)*.2 * sm*2.13;
      	// Mechanics... a butchered d = vt + (1/2)at^2    ;)
      	pos.y += (.1 - (.075+hash(i*30.0+rnd*36.7)*.15)*(sm*sm)*.8);
      	float d = RockParticle(pos, uv, .01*hash(i*1332.23)+.001, (hash(-i*42.13*rnd)-.5)*15.0);
      	if (d <= 0.0) continue;
      	float c = max(.3+abs(hash(i*11340.0))*.8+(1.0-sm*.5), 0.0);
      	col = mix(col, vec3(c,c*.2, 0.0), min(d, 1.));
      }

      // Loop through smoke particles...
      for (float i = 0.0; i < 120.0; i+=1.0)
      {
      	// Lots of magic numbers? Yerp....
      	float t=  time+i*(2.+hash(i*-1239.)*2.0);
      	float sm = mod(t, 8.6) *.5;
      	float rnd = floor(t / 8.6);

      	vec2 pos = vec2(0.0, sm) *.5;
      	pos.x += (hash(i)-.5)*.2 * uv.y*5.13;
      	float d = SmokeParticle(pos, uv, .03*hash(i*1332.23+rnd)+.001+sm*0.03, hash(i*rnd*2242.13)-0.5);
      	if (d <= 0.0) continue;
      	d = d* max((3.0-(hash(i*127.0)*1.5) - sm*.63), 0.0);
      	float c = abs(hash(i*4.4));
      	// Black/rusty smoke...
      	col = mix(col, vec3(c*.3+.05, c*.3, c*.25), min(d, 1.0));
      	// Lava gush...
      	col = mix(col, vec3(.52, .25, 0.0), max((d-1.05)*8.0, 0.0));
      }

      uv = texcoord.xy;
      col *= pow( 45.0*uv.x*uv.y*(1.0-uv.x)*(1.0-uv.y), .08 );

      p3d_FragColor = vec4(col, 1.0);

}
