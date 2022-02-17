#version 140
in vec4 l_texcoord0; //TEXCOORD0,
in vec4 l_texcoord1; //TEXCOORD1,
in vec4 l_texCoordReflec; //TEXCOORD2,
in vec4 l_eye_normal; //TEXCOORD3
in vec4 l_eye_position; // TEXCOORD4,

uniform sampler2D p3d_Texture0; // TEXUNIT0
uniform sampler2D water_norm;
uniform sampler2D water_alpha;
uniform mat4 dlight0;

out vec4 o_color;

void main()
{
   vec4 distortion1 = normalize(texture2D(water_norm, l_texcoord0.xy));
   vec4 distortion2 = normalize(texture2D(water_norm, l_texcoord1.xy));

   float alpha=texture2D(water_alpha, l_texcoord0.xy).r+texture2D(water_alpha, l_texcoord1.xy).r;

   float facing = 1.0- max(dot(normalize(-l_eye_position.xyz), normalize(l_eye_normal.xyz)), 0);

   vec4 normalmap=distortion1+distortion2;
   vec3 tsnormal = (normalmap.xyz * 2) - 1;
   vec4 c_eye_normal;
   c_eye_normal.xyz = l_eye_normal.xyz * tsnormal.z;
   c_eye_normal.xyz += vec3(1,0,0) * tsnormal.x;
   c_eye_normal.xyz += vec3(0,1,0) * tsnormal.y;
   c_eye_normal.xyz = normalize(c_eye_normal.xyz);

   vec4 lhalf = dlight0[3];
   vec4 lcolor=dlight0[0];
   float shine=150;
   vec4 lspec=dlight0[1];//not sure whats this
   float factor=0.1;
   float dotProd = dot(c_eye_normal.xyz, lhalf.xyz);
   vec4 specular = pow(clamp(dotProd, 0.0, 1.0), shine)*lcolor*lspec;
   vec4 texProj = textureProj(p3d_Texture0, l_texCoordReflec+distortion1*distortion2*10);
   o_color = mix(texProj, specular, factor);
   o_color.a=alpha+(facing*0.4)-0.1;
}
