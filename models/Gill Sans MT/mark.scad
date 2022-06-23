//------------------------------------------------------
// Mark
// Simple texte
// 5@xes 04/06/2022
// Size Must be 1x1 !
//------------------------------------------------------

$fn=30;
// font = "Gill Sans MT:style=Bold";
// font = "Roboto:style=Bold";
// font = "Leelawadee:style=Bold";
// font = "Arial Rounded MT Bold:style=Bold";
font = "Gill Sans MT:style=Bold";


letter_height = 1;
letter_size =1;

render() translate([0,0,0]) letter("«");


module letter(Txt) {
  color("Red")
  linear_extrude(height = letter_height) {
    text(Txt, size = letter_size, font = font, halign = "left", valign = "baseline");
  }
}                