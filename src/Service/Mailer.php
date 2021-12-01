<?php

namespace App\Service;

class Mailer
{

// source https://usefulscripts.wordpress.com/2007/10/20/sending-emails-with-asp-and-php/

    public function createMailer($local = false) {
        $mailer  = new \COM('CDO.Message') or die("unable to initiate mailer");
        $config = new \COM('CDO.Configuration') or die("unable to initiate mailer");
    
        $pickup_directory = "e:\\system\\mailroot\\Pickup\\";
    
        if ($local) {
            $pickup_directory = "c:\\inetpub\\mailroot\\Pickup\\";
        }
    
        $config->Fields['http://schemas.microsoft.com/cdo/configuration/sendusing'] = 1;
        $config->Fields['http://schemas.microsoft.com/cdo/configuration/smtpserverpickupdirectory'] = $pickup_directory;
        $config->Fields->Update();
    
        $mailer->Configuration = $config;
    
        return $mailer;
    }

}
