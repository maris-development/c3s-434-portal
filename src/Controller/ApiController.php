<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use App\Service\ApplicationLibrary;
use Symfony\Component\HttpFoundation\JsonResponse;

class ApiController extends AbstractController
{

    private $lib;
    private $options;

    public function __construct(ApplicationLibrary $lib) {
        $this->lib = $lib;
        $this->options = $this->lib->GetDefaultOptions(readHtml: true);
    }
    
    

    public function getHistory(string $identifier = "", string $type = "") {
        if(!$identifier || !$type) return new JsonResponse([], 404);

        $result = $this->getHistoryObj($identifier, $type);

        if(!$result) return new JsonResponse([], 404);

        $response = new JsonResponse($result);

        $response->setEncodingOptions( $response->getEncodingOptions() | JSON_PRETTY_PRINT );

        return $response;

    }

    public function getHistoryObj(string $identifier = "", string $type = "", string $indicatorType = "", $limit = 0){

        $queryBuilder = $this->lib->conn->createQueryBuilder();

        $fields = "tl.input_date , tl.c3s_indicator_id , tl.c3s_indicator_type , tl.c3s_request_type , 
        tl.request_url , tl.request_method , tl.request_content , tl.response_status , tl.response_duration , 
        tm.title ,  tm.ecde_url";
        
        $logtable = $this->lib->dbTables['c3s_api_testlog'];
        $metatable = $this->lib->dbTables['c3s_api_metadata_static'];

        $queryBuilder->select($fields)
            ->from("$logtable AS tl, $metatable AS tm")
            ->where("tl.c3s_indicator_id = :identifier")
            ->andWHere("tl.c3s_indicator_id = tm.c3s_identifier")
            ->andWhere("tl.response_status <> 1200")
            ->andWhere("datediff(d, tl.input_date, getdate()) <= 7")
            ->orderBy("tl.input_date", "DESC")
            ->setParameter("identifier", $identifier);

        if($type != 'any'){
            $queryBuilder->andWhere("tl.c3s_request_type = :type")
                ->setParameter("type", $type);
        }

        if($indicatorType){
            $queryBuilder->andWhere("tl.c3s_indicator_type = :indicatorType")
                ->setParameter("indicatorType", $indicatorType);
        }

        if($limit > 0) {
            $queryBuilder->setMaxResults($limit);
        }

        $stmt = $queryBuilder->execute();

        return $stmt->fetchAll();
    }
    
    public function getTable() {
        $result = $this->getTableObj();

        if(!$result) return new JsonResponse([], 404);

        $response = new JsonResponse($result);

        $response->setEncodingOptions( $response->getEncodingOptions() | JSON_PRETTY_PRINT );

        return $response;
    }

    public function getTableObj() {
        
        $queryBuilder = $this->lib->conn->createQueryBuilder();
        
        $logtable = $this->lib->dbTables['c3s_api_testlog'];

        $queryBuilder->select('distinct c3s_indicator_id, c3s_indicator_type, c3s_request_type')
            ->where("c3s_request_type = 'workflow_execution'")
            ->from("$logtable")
            ->orderBy("1");

        $stmt = $queryBuilder->execute();
        $distinct = $stmt->fetchAll();
        
        $data = array();
        
        foreach($distinct as $row){
            $history = $this->getHistoryObj($row['c3s_indicator_id'], $row['c3s_request_type'], $row['c3s_indicator_type']);
            if($history){
                $history = $this->rateHistory($history);

                $result = $history[0];
                
                $result['history'] = $history;

                $data[$row['c3s_indicator_id']][$row['c3s_indicator_type']] = $result;
            }
        }

        return $data;
    }

    public function rateHistory($logs){
        for($i = 0; $i < count($logs); $i++){
            $logs[$i] = $this->rateRequest($logs[$i]);
        }
        return $logs;
    }

    public function rateRequest($log){
        $timeout = 10 * 60 * 1000;

        switch($log['response_status']){
            case '200':
                $log['status'] = 'green';

                if(intval($log['response_duration']) > $timeout){
                    $log['status'] = 'red';
                } else if (intval($log['response_duration']) > $timeout / 2 ) {
                    $log['status'] = 'orange';
                }
                break;
            default:
                $log['status'] = 'red';    
        }    

        $log['request_content'] = json_decode($log['request_content']);
        $log['request_content_qs'] = http_build_query($log['request_content']);

        return $log;
    }
}
