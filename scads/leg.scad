leg(23,12.5);

module leg(sl,sw){
	height=8;
	difference(){
		//solid parts
		union(){
			hull(){
				//main inner square
				translate([-30,-10,0]) cube([28,20,height]);
				//lower taper
				translate([5,-1.5,0]) cube([2,3,height]);
			}
	
			//leg
			translate([0,-1.5,0]) cube([40,3,height]);
			//top bar
			translate([-33,-7,0]) cube([6,14,height]);
			//rounded corners
			for (i = [ [-30,7,0],[-30,-7,0] ]){
				translate(i) cylinder(r=3,h=height,$fn=50);
			}	
		}
		//servo mounts
		for (i = [ [-3,0,-2],[-31,0,-2] ]){
			translate(i) cylinder(r=1,h=20,$fn=20);
		}
		//hole for servo body
		translate([-17,2.5,2])  cube([sl,sw+5,22], center=true);
	}
}


