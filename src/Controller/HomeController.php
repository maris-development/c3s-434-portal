<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use App\Service\ApplicationLibrary;
use App\Repository\NewsRepository;


class HomeController extends AbstractController
{
    private $lib;
    private $api;
    private $options;

    public function __construct(ApplicationLibrary $lib, ApiController $api) {
        $this->lib = $lib;
        $this->api = $api;
        $this->options = $this->lib->GetDefaultOptions();
    }
    

    public function index(): Response
    {   
        $this->options['c3s_metadata'] = $this->getMetaData();
        $this->options['c3s_testresults'] = $this->api->getTableObj();
        $this->options['meta']['canonical_url'] = $this->lib->httpHost . "/home";
        
        return $this->lib->renderWithCache('home.html.twig', $this->options);
    }

    private function getMetaData(){
        $queryBuilder = $this->lib->conn->createQueryBuilder();

        $queryBuilder->select("c3s_identifier, ecde_url, title")
            ->from($this->lib->dbTables['c3s_api_metadata_static'])
            ->orderBy("c3s_identifier");

        $stmt = $queryBuilder->execute();

        return $stmt->fetchAll();
    }

        
    public function http404NotFound(): Response 
    {
        return $this->lib->httpErrorResponse(404, 'Page not found');
    }
}
