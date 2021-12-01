<?php

	set_time_limit(6000);

  $IP = $_SERVER['REMOTE_ADDR'];

	if (substr($IP,0,3) == '10.' or $IP == '81.173.96.49' or $IP == '81.173.61.180') {

		rrmdir('../var/cache/');
		print "Done... ($IP)";

	} else {
		print "You are not allowed to call this page";
	}

function rrmdir($dir) {
   if (is_dir($dir)) {
     $objects = scandir($dir);
     foreach ($objects as $object) {
       if ($object != "." && $object != "..") {
         if (is_dir($dir."/".$object) && !is_link($dir."/".$object))
           rrmdir($dir."/".$object);
         else
           unlink($dir."/".$object);
       }
     }
     rmdir($dir);
   }
 }
/*============================================*/
/*============================================*/
?>
