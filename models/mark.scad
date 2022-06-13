//------------------------------------------------------
// Mark
// Simple texte
// 5@xes 04/06/2022
//------------------------------------------------------

$fn=30;
// font = "Roboto:style=Bold";
// font = "Leelawadee:style=Bold";
font = "Gill Sans MT:style=Bold";

letter_height = 1;
letter_size =1;

render() translate([0,0,0]) letter("ß");


module letter(Txt) {
  color("Red")
  linear_extrude(height = letter_height) {
    text(Txt, size = letter_size, font = font, halign = "left", valign = "baseline");
  }
}                