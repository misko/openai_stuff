backbone(90,14,8,23,12.5);

module backbone(bl,bw,bh,sl,sw){
	h_pos = ((bl-20) / 2);		
	difference(){
		// main
		
		union() {
			difference() {
				translate([-(bw/2),-(bl/2),-(bh/2)]) color("purple") cube([bw,bl,bh]);
				//round side indents
				for (i = [[34,17,-5],[34,-17,-5],[-34,17,-5],[-34,-17,-5]]) {
					translate(i) cylinder(r=30,h=10,$fn=200);
				}
			}
			translate([0,h_pos,0]) hip(23,12.5);
			translate([0,-h_pos,0]) hip(23,12.5);
		}
			
		

		//servo body cutouts
		for (i = [[-16.5,h_pos+5,0],[16.5,h_pos+5,0],[-16.5,-h_pos-5,0],[16.5,-h_pos-5,0]]){
			translate(i) #cube([sl,sw+10,bh], center=true);
		}		

		//servo mount holes
		for (i = [[2.5,h_pos,-10],[-2.5,h_pos,-10],[-2.5,-h_pos,-10],[2.5,-h_pos,-10]]){
			translate(i) cylinder(r=1,h=20,$fn=20);
		}

		//center hole
		translate([0,0,-5]) cylinder(r=3,h=12,$fn=200);
	}
}

module hip(l,w){
   height = 8;
   difference(){
      translate([0,0,-height/2]) union(){
         //main
         translate([-29,-12,0]) cube([58.5,24,height]);

         //outside edges
         for (i = [[-32.5,-8.5,0],[26.5,-8.5,0]] ){
         	   translate(i) cube([6,17,height]);
         }

         //rounded corners
         for (i = [[-29.5,9,0],[-29.5,-9,0],[29.5,9,0],[29.5,-9,0]] ){
            translate(i) cylinder(r=3,h=height,$fn=50);
         }
      }
      
      //servo mount holes
      for (i = [[-2.5,0,-2],[-30.5,0,-2],[2.5,0,-2],[30.5,0,-2]] ){
         translate(i) cylinder(r=1,h=200,$fn=20);
      }
      
      //servo body cutouts
      for (i = [[-16.5,0,2],[16.5,0,2]] ){
         translate(i)  cube([l,w,22], center=true);
      }

   }
}
