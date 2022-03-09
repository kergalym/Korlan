const float pi = 3.1415926535;

// of equation x^3+c1*x+c2=0
/* Stolen from http://perso.ens-lyon.fr/christophe.winisdoerffer/INTRO_NUM/NumericalRecipesinF77.pdf,
   page 179 */
float cubicRoot(float c1, float c2) {
	float q = -c1/3.;
	float r = c2/2.;
	float q3_r2 = q*q*q - r*r;
	if(q3_r2 < 0.) {
		float a = -sign(r)*pow(abs(r)+sqrt(-q3_r2),.333333);
		float b = a == 0. ? 0. : q/a;
		float x1 = a+b;
		return x1;
	}
	return 0.;
	/*float theta = acos(r/pow(q,1.5));
	float sqr_q = pow(q,.5);
	vec3(-2.*sqr_q*cos(theta/3.),
		 -2.*sqr_q*cos((theta+2.*pi)/3.),
		 -2.*sqr_q*cos((theta-2.*pi)/3.));*/
}

float arcLength(float a, float b, float x) {
	float f = .25/a;
	float h = x/2.;
	float q = length(vec2(f,h));
	return h*q/f+f*log((h+q)/f);
}

vec2 parabolaCoords(float a,float b,vec2 co) {
	float x = cubicRoot((1./a-2.*co.y+2.*b)/(2.*a),(-co.x)/(2.*a*a));
	return vec2(length(co-vec2(x,a*x*x+b)),arcLength(a,b,x));
}

float noise3(vec3 co){
  return fract(sin(dot(co ,vec3(12.9898,78.233,125.198))) * 43758.5453);
}

float smooths(float v) {
	return 3.*pow(v,2.)-2.*pow(v,3.);
}

float perlin3(vec3 p) {
	float val = 0.;
	for(float i=0.;i<3.;i += 1.){
		p *= pow(2.,i);
		vec3 c = floor(p);
		float u = smooths(fract(p.x));
		float v = smooths(fract(p.y));
		val = 1.-((1.-val)*(1.-pow(.5,i)*
			mix(mix(mix(noise3(c),noise3(c+vec3(1.,0.,0.)),u),
					mix(noise3(c+vec3(0.,1.,0.)),noise3(c+vec3(1.,1.,0)),u),v),
			    mix(mix(noise3(c+vec3(0.,0.,1.)),noise3(c+vec3(1.,0.,1.)),u),
					mix(noise3(c+vec3(0.,1.,1.)),noise3(c+vec3(1.,1.,1.)),u),v),fract(p.z))));
	}
	return val;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
	vec2 uv = fragCoord.xy / iResolution.x;
	vec2 r = uv-(iResolution.xy/iResolution.x)*vec2(.5,.3);
	r *= 6.;
	r = parabolaCoords(1./3.,0.,r);
	r.x = pow(r.x*.8+.7,3.);
	float l = exp(-r.x*1.8)+.01/(r.x-.33);
	r.x -= iTime*3.;
	float v = perlin3(vec3(r,iTime));
	vec4 c = vec4(vec3(v*1.,v*1.+0.6*cos(.5*iTime),v*(.5*sin(iTime)+.5)*2.5)*l,v);	
	
	fragColor = c;
}
