#version 120

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord.xy / iResolution.xy;

	float amount = 0.0;

	amount = (1.0 + sin(iTime*6.0)) * 0.5;
	amount *= 1.0 + sin(iTime*16.0) * 0.5;
	amount *= 1.0 + sin(iTime*19.0) * 0.5;
	amount *= 1.0 + sin(iTime*27.0) * 0.5;
	amount = pow(amount, 3.0);

	amount *= 0.05;

    vec3 col;
    col.r = texture( iChannel0, vec2(uv.x+amount,uv.y) ).r;
    col.g = texture( iChannel0, uv ).g;
    col.b = texture( iChannel0, vec2(uv.x-amount,uv.y) ).b;

	col *= (1.0 - amount * 0.5);

    fragColor = vec4(col,1.0);
}