//------------------------------------------------------
// Mark
// Simple texte
// 5@xes 24/06/2022
// Size Must be 1x1 !
//------------------------------------------------------
use <NameItRounded-Bold.ttf>

$fn=20;

font = "NameItRounded-Bold:style=Bold";


letter_height = 1;
letter_size =1;

//render() translate([0.5,0,0]) mirror([1,0,0]) letter("/");
render() translate([0,0,0]) letter("J");


module letter(Txt) {
  color("Red")
  linear_extrude(height = letter_height) {
    text(Txt, size = letter_size, font = font, halign = "left", valign = "baseline");
  }
}                