//9g generic
//shoulder(26,5.5,3.5,2,13);
//tower servo
translate([0,0,19.5]) rotate([0,-90,0]) shoulder(27,7,4,2.5,15);

module hornbracket(hr_st,hh,hrd,hr1,hr2) {
	//horn bracket
	translate([hr_st,0,0]) difference(){
		union(){
			translate([0,22,-3]) rotate([55,0,0]) cube([5,15,hh+18]);
			//vert wall
			//translate([hr_st-4,-8,0]) cube([9,31.5,hh+.35+8]);
			//round top
			//translate([hr_st,0,hh+.35]) rotate([0,90,0]) cylinder(r=8, h=5, $fn=100);
			
		}
		translate([10,19.5,-5]) rotate([0,0,90]) cube([15,16,hh+15]);
		//servo horn hole
		translate([0,0,hh]) rotate([0,90,0]) cylinder(r=hr1,h=6,$fn=100);
		//servo horn channel
		translate([-1,0,hh]) rotate([55,0,0]) hull(){	
			//top channel
			translate([-2,-3.5,0]) cube([5,7,9]);
			//large round
			translate([0,0,0]) rotate([0,90,0]) cylinder(r=hr1,h=3,$fn=100);	
			//small round
			translate([0,0,-hrd]) rotate([0,90,0]) cylinder(r=hr2,h=3,$fn=100);
		}
		
	}
}

module shoulder(st,sc,hr1,hr2,hrd){
	// st = servo tall gap
	// cc = servo clearance from inside wall
	// hr1 = horn radius1
	// hr2 = horn radius2
	// hrd = distance between horn radii

	//bottom plate constants
	plate_thick = 3.5;
	offset_x = 4; offset_y = 4;
	m3_screw_dia = 3;
	m3_screw_head_dia = 7;
	m3_screw_head_height = 1.75;
	m3_nut_wrench_size = 6.5;
	m3_nut_height = 1.75;

	//calc'd starts
	ch_st = (st/2)-1;
	hr_st = -((st/2)+6);

	hh = sc+14.15;

	//channel bracket
	/*difference(){
		union(){
			//vert wall
			translate([ch_st,-8,0]) cube([6,16,hh+.35]);
			//round top
			translate([ch_st,0,hh+.35]) rotate([0,90,0]) cylinder(r=8, h=6, $fn=100);
		}
		// button hole bottom
		translate([ch_st,0,hh]) rotate([0,90,0]) cylinder(r=3,h=6,$fn=100);		
		// button hole top
		translate([ch_st-2,0,hh-.1]) rotate([0,90,0]) cylinder(r=5.6,h=3,$fn=100);	
		//bottom channel
		translate([ch_st+5,-5,-1]) cube([2,10,30]);
	}*/
	


	difference(){
		//intersection() {
			union() {
				hornbracket(hr_st,hh,hrd,hr1,hr2);
				rotate([0,180,90]) hornbracket(hr_st,hh,hrd,hr1,hr2);
				translate([-19.5,9.5+5,2.5]) rotate([0,90,0]) cube([10,5,5]);
			
				
				//translate([-23.5,20,-23.5]) rotate([90,0,0]) cylinder(r=5,h=80,$fn=100);
			}
	
			//translate([-23,25,-40]) cylinder(r=33,h=80,$fn=100);
		//}
		//translate([-38,14,-10]) rotate([0,55,0]) cube([40,15,15]);
		//	translate([8,-8,-40]) cylinder(r=22.5,h=80,$fn=100);
		//	translate([-24,8.5,14]) cube([12,18,30]);
		//	translate([-40,23,18.5]) rotate([0,90,0]) cylinder(r=15,h=80,$fn=100);
		//main plate
		//translate([-19,-8,0]) cube([37,16,plate_thick]);
		//screw holes
		//for (i = [[offset_x-.5,offset_y,-1],[offset_x-.5,-offset_y,-1],[-offset_x-.5,offset_y,-1],[-offset_x-.5,-offset_y,-1]]){	
		//	translate(i) cylinder(r=m3_screw_dia/2, h=plate_thick+2, $fn=20);
		//}
		//screw head holes
		//for (i = [[offset_x-.5,-offset_y,plate_thick-m3_screw_head_height+.1],[-offset_x-.5,-offset_y,plate_thick-m3_screw_head_height+.1]]){
		//	translate(i) cylinder(r=m3_screw_head_dia/2, h=m3_screw_head_height, $fn=20);
		//}
		//nut traps
		//for (i = [[offset_x-.5,offset_y,plate_thick-m3_nut_height+.1],[-offset_x-.5,offset_y,plate_thick-m3_nut_height+.1]]){
		//	translate(i) cylinder(r=m3_nut_wrench_size/2, h=m3_nut_height, $fn=6);
		//}
	}
}
