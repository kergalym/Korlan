#version 430    

layout (local_size_x = 8, local_size_y = 4) in;
layout (r32f) uniform image2D depthLODTex;
uniform ivec2 offset;

void main() {

  ivec2 del=ivec2(1,0);
  ivec2 Coord = ivec2(gl_GlobalInvocationID.x*2+1,gl_GlobalInvocationID.y*2+offset.x);
  ivec2 CoordLOD = ivec2(gl_GlobalInvocationID.x+1,gl_GlobalInvocationID.y+offset.y);
  float z_x00_y00,z_x01_y00,z_x00_y01,z_x01_y01,zmin;
  z_x00_y00 = imageLoad(depthLODTex, Coord).x;
  z_x01_y00 = imageLoad(depthLODTex, Coord+del.xy).x;
  z_x00_y01 = imageLoad(depthLODTex, Coord+del.yx).x;
  z_x01_y01 = imageLoad(depthLODTex, Coord+del.xx).x;
  zmin = min(min(z_x00_y00,z_x01_y00),min(z_x00_y01,z_x01_y01));
  imageStore(depthLODTex,CoordLOD,vec4(zmin));
} 
