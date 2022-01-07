<?php
//===================================================================
// bb 202000928
// created Application_library.php
//
// All application related properties and methods
//===================================================================

namespace App\Service;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use Symfony\Component\Form\Extension\Core\Type\EmailType;
use Symfony\Component\Form\Extension\Core\Type\SubmitType;
use Symfony\Component\Form\Extension\Core\Type\CheckboxType;
use Symfony\Component\Form\Extension\Core\Type\FormType;
use Symfony\Component\Form\FormBuilderInterface;

use Symfony\Component\Security\Core\Security;

use Doctrine\ORM\EntityManagerInterface;
use Symfony\Component\DependencyInjection\ContainerInterface;
use Symfony\Component\HttpFoundation\RequestStack;
use Symfony\Component\HttpFoundation\Response;
use Twig\Extension\AbstractExtension;
use Twig\TwigFunction;
use Symfony\Component\Security\Http\Authentication\AuthenticationUtils;
use Symfony\Component\Routing\Generator\UrlGeneratorInterface;

class ApplicationLibrary extends AbstractExtension
{


    public $DefaultContent = array(
        "project_title"    => "ECDE API Monitoring overview",
        "project_abbreviation"    => "C3S-434-TTD",
        "project_description"    => "Testing the C3S Toolbox workflows published for ECDE",
        "current_menu"     => "home",
        "meta_description" => "",
        "meta_keywords"    => "",
        "pageSize"         => 10,
        "currentPage"      => 1,
        "login"            => false,
        "user"             => array(),
        "local"            => false,
        "read_html"        => false,
        "html"             => array(),
        "user"             => false,
    );

    public $local = false;

    public $menus = array(
        'home'      => array(
            'label'   => 'Home',
            'class'   => '',
            'action'  => '/',
            'active'  => false,
            'new_tab' => false,
        )
    );

    public $media_path = '/media/c3s_api_tester_stats/';

    public $media = array(
        'algemeen gebruik' => 'img_300_222/',
        'wysiwyg'          => 'img_800_800/',
    );

    public $dbTables = [
        "c3s_api_testlog" => "c3s_api_testlog",
        "c3s_api_metadata"    => "c3s_api_metadata",
        "c3s_api_metadata_static"    => "c3s_api_metadata_static",
    ];


    public RequestStack $requestStack;
    public EntityManagerInterface $entityManager;
    public EntityManagerInterface $entityManagerWrite;
    public ContainerInterface $container;
    public AuthenticationUtils $authenticationUtils;
    public Security $security;
    public UrlGeneratorInterface $urlGenerator;
    public $httpHost;

/****************************************************************/
    public function __construct(
        EntityManagerInterface $entityManager, 
        EntityManagerInterface $entityManagerWrite, 
        RequestStack $requestStack, 
        ContainerInterface $container,
        Security $security,
        AuthenticationUtils $authenticationUtils,
        UrlGeneratorInterface $urlGenerator
    ) {
/****************************************************************/
        $this->requestStack = $requestStack;
        $this->request      = $this->requestStack->getCurrentRequest();

        $this->container          = $container;
        $this->entityManager      = $entityManager;
        $this->entityManagerWrite = $entityManagerWrite;
        $this->conn               = $entityManager->getConnection();

        $this->security             = $security;
        $this->authenticationUtils = $authenticationUtils;
        $this->urlGenerator = $urlGenerator;
        
        $this->local = $this->isLocal();
        $this->user = $this->security->getUser(); // in twig is het app.user (symfony default)

        
    }

/****************************************************************/
    public function GetDefaultOptions($opt_params = array(), $readHtml = false)
    {
/****************************************************************/

// get the default content

        $options = $this->DefaultContent;

        //haal host op
        $httpHost = $this->request->getSchemeAndHttpHost();
        
        if(!$this->local){  
            $httpHost = str_replace('http://', 'https://', $httpHost);   
        }

        $this->httpHost = $options['http_host'] = $httpHost;

// zet gegeven parameters erbij

        $options = array_merge($options, $opt_params);

// zet local er in
        $options['local'] = $this->local;

//read html parameter
        $options['read_html'] = $readHtml;

// build breadcrumb

        $this->breadcrumbs    = [];
        $this->breadcrumbs[0] = "home";

        $this->pathInfo = explode('/', $this->request->getPathInfo());
        array_shift($this->pathInfo); //remove first empty string
        $options['current_menu'] = $this->pathInfo[0];

        if (array_key_exists($options['current_menu'], $this->menus)) {
            $this->menus[$options['current_menu']]['active'] = true;
        }

        $dashesToSpaces = fn($str) => str_replace('-', '-', $str);

        $this->breadcrumbs = array_merge($this->breadcrumbs, $this->pathInfo);
        $this->breadcrumbs = array_map($dashesToSpaces, $this->breadcrumbs);

        $options['breadcrumbs'] = $this->breadcrumbs;

// if html request
        if ($options['read_html']) {

            $readHtml = array();

// lees indien nodig de html pagina bij het menu
            if (empty($readHtml)) {
                $readHtml = $this->readHtmlPage($options['current_menu']);
            }

            $options['html'] = $readHtml;

            if($options['html'] && $options['html']['title']){
               $this->changeLastBreadCrumbsValue($options, $options['html']['title']); 
            }
        }

        $options['menus']      = $this->menus;
        $options['menus_keys'] = array_keys($this->menus);

        $options['meta'] = $this->createMetaData($options);
        $options['default_email_signup_form'] = $this->createNewsletterSignupFormView();

        // dump($options);die;
        return $options;
    }

    public function createMetaData($options){
        //creeer metadata voor in meta-tags.html.twig
        //meta.title 

        return [
            "site_name" => $options['project_title'],
            "url" => strtok($this->request->getUri(), '?'),
            "image" => "",
        ];
    }

    public function createNewsletterSignupForm() 
    {

        $form = $this->createFormBuilder([])
            ->setAction("/newsletter/signup")
            ->add('name', TextType::class, array('required' => false, "attr" => ["placeholder" => "Name (not required)"]))
            ->add('email', EmailType::class, array("attr" => ["placeholder" => "E-mail address"]))
            ->add('agreement', CheckboxType::class, array(
                "label" => "I give my consent", 
                "attr" => ["class" => ""],
                // 'expanded' => true, 
                'label_attr' => ['class' => 'inline-label']
            ))
            ->add('send', SubmitType::class, array("attr" => ["class" => "secondary-button"]))
            ->getForm();

        return $form;
    }

    public function createNewsletterSignupFormView(){
        return $this->createNewsletterSignupForm()->createView();
    }


/****************************************************************/
    public function readHtmlPage($identifier)
    {
/****************************************************************/
        return;
// lees een html pagina op de rewrtie_url
// of op de n_code om de rewrite_url op te halen sh 20200904. Bijvoorbeeld voor de redirect naar de thankyou vanuit het contact form
// indien geen meta info dan return default

        $c_fields     = '*';
        $queryBuilder = $this->conn->createQueryBuilder();
        //SELECT TOP 1 * FROM tab_html_page WHERE menu = 'about' ORDER BY n_code DESC
        if (is_numeric($identifier)) {
            // $queryBuilder->select($c_fields)
            //     ->from($this->dbTables['html_page'])
            //     ->where("n_code = :n_code")
            //     ->setParameter(":n_code", $identifier)
            //     ->orderBy("1", "desc");
        } else {
            // $queryBuilder->select($c_fields)
            //     ->from($this->dbTables['html_page'])
            //     ->where("menu = :menu")
            //     ->setParameter(":menu", $identifier)
            //     ->orderBy("1", "desc");
        }

        $stmt = $queryBuilder->execute();

        $result = $stmt->fetchAll();
        $html   = array();

        if ($result) {
            $html = array_filter($result[0]);
        }

        return $html;
    }

//********************************************************************
    public function get_menu()
    {
//********************************************************************

        return $this->menus;

    }

//********************************************************************
    public function get_menu_link($MenuKey, $UrlLabel = '', $Querystring = '')
    {
//********************************************************************

        $return = '';

        if (isset($this->menus[$MenuKey])) {
            $Url   = $this->menus[$MenuKey]['action'];
            $Label = $this->menus[$MenuKey]['label'];

            if ($UrlLabel != '') {
                $Label = $UrlLabel;
            }

            if ($Querystring != '') {
                if (substr($Url, -1) != '/') {
                    $Url .= '/';
                }
                $Url .= $Querystring;
            }

            $return = '<a href="' . $Url . '" title="Ga naar:' . $Label . '">' . $Label . '</a>';
        }
        return ($return);

    }

//********************************************************************
    public function isLocal()
    {
//********************************************************************
//----------------------------------------------
// test of local
//----------------------------------------------

        $return = false;
        $c_ip   = "";

        if (isset($_SERVER['LOCAL_ADDR'])) {
            $c_ip = $_SERVER['LOCAL_ADDR'];

        } else if ($this->request) {
            $c_ip = $this->request->getClientIp();
            
        }

        if (strpos($c_ip, '77.87.163') === false and strpos($c_ip, '212.189.40') === false and strpos($c_ip, '212.189.1') === false and strpos($c_ip, '194.41.62') === false) {
            $return = true;
        }
        return $return;
    }

//--------------------------------------------------------------------
// hierdoor kunnen de functies ook in een twig gebruikt worden
//--------------------------------------------------------------------

//********************************************************************
    public function getFunctions()
    {
//********************************************************************
        return [
//        new TwigFunction('addParam', [$this, 'filterPath']),
//        new TwigFunction('paging_number', [$this, 'paging_number']),
            new TwigFunction('get_global', [$this, 'get_global']),
            new TwigFunction('get_menu_link', [$this, 'get_menu_link']),
            new TwigFunction('get_menu', [$this, 'get_menu']),
        ];
    }

//===================================================================
// bb 20200707
// functie op alle mogelijk locale ($this) variabelen op te halen
//===================================================================

    public function get_global($property)
    {

        $return = 'property does not exists';

        if (property_exists($this, $property)) {
            $return = $this->{$property};
        }
        return ($return);
    }

    public function put_global($property, $value)
    {

        $return = 'property does not exists';

        if (property_exists($this, $property)) {
            $this->{$property} = $value;
            $return            = $this->{$property};
        }
        return ($return);
    }

//********************************************************************
    public function replace_if_filled($dest, $value)
    {
//********************************************************************
        $return = $dest;
        if ($value != '') {
            $return = $value;
        }
        return $return;

    }

    public function libAppendLog($p, $desc='') {
        //fallback
      $this->appendLog($p, $desc);
    }
  
    public $logAttributes = array(
          'location' => 'e:/system/logfiles/php_script/',
          'logname' => 'php_script',
          'extension' => '.log'
    );

    //********************************************************************
    public function appendLog($p, $desc='') {
    //********************************************************************


        // Build filename
        $date = date("ymd");
        $filename = $this->logAttributes['location'] . $this->logAttributes['logname'] . '_' . $date . $this->logAttributes['extension'];

        @mkdir($this->logAttributes['location']);


        // build backtrace
        $backtrace = debug_backtrace(DEBUG_BACKTRACE_PROVIDE_OBJECT, 2);
        $file = basename($backtrace[1]['file']);
        $line = $backtrace[1]['line'];
        $caller_function = $backtrace[1]['function'];
        $date = date("y-m-d H:i:s");

        // Write log
        $handle = fopen($filename, "a");
        
        fwrite($handle, "$date (TAObserver.com) ($file:$line function $caller_function)");

        if ($desc) fwrite($handle, ' ('.$desc.')');
        
        fwrite($handle, ': ');
        
        switch(true) {

            case is_array($p):
                if (!empty($p)) {
                    $temp = print_r($p, true);
                    fwrite($handle, $temp);
                }
                break;
            case method_exists($p, '__toString'):
            case is_a($p, 'Throwable'):
                if (!empty($p)) {
                    $temp = $p->__toString();
                    fwrite($handle, $temp);
                }
                break;

            default:
                fwrite($handle, $p);
                break;
        }

        fwrite($handle, chr(10));
        fclose($handle);
    }

//********************************************************************
    public function changeLastBreadCrumbsValue(&$options, $title)
    {
//********************************************************************
        // Set last name of the bread crumbs instead of showing URL Slug
        $lastIdx                          = count($options['breadcrumbs']) - 1;
        $options['breadcrumbs'][$lastIdx] = $title;
    }

//********************************************************************
    public function calculatePagination($count, $pageSize, $page, $url = '/%PAGE%')
    {
//********************************************************************
        $pagination = array(
            "found" => $count,
            "page" => $page,
            "limit" => $pageSize,
            "offset" => ($page - 1) * $pageSize,
            "pages" => intval(ceil($count/$pageSize)),
            "url" => $url
        );     

        if($pagination['page'] > $pagination['pages'] || $pagination['page'] < 1){
            $this->httpErrorResponse( 404, 'Page ' . $page . ' not found', ['pagination' => $pagination])->send();
            die;
        }

        return $pagination;
    }

    

//********************************************************************
    public function httpErrorResponse($responseCode, $message, $options = []): Response
    {
//********************************************************************
        $options = $this->GetDefaultOptions($options);

        $options['http_code']     = $responseCode;
        $options['error_message'] = $message;
        
        $response = $this->render('error/http-error.html.twig', $options);

        $response->setStatusCode($responseCode);

        switch($responseCode){
            case 401:
                //voorkom de login box op 401 met deze header.
                $response->headers->set('WWW-Authenticate', 'Cookie');
                break;
        }

        return $response;
    }
    

//********************************************************************
public function getCookie(string $cookieName)
{
//********************************************************************
    $cookies = $this->request->cookies;

    if ($cookies->has($cookieName))
    {
        return $cookies->get($cookieName);
    }

    return false;
}


//********************************************************************
// Transliteratie functie e.g. 
// America Móvil to Seek Annulment of ICSID Arbitration Award -> america-movil-to-seek-annulment-of-icsid-arbitration-award
// Veilig maken voor URL's 
    public static  $transliterationTable = array('á' => 'a', 'Á' => 'A', 'à' => 'a', 'À' => 'A', 'ă' => 'a', 'Ă' => 'A', 'â' => 'a', 'Â' => 'A', 'å' => 'a', 'Å' => 'A', 'ã' => 'a', 'Ã' => 'A', 'ą' => 'a', 'Ą' => 'A', 'ā' => 'a', 'Ā' => 'A', 'ä' => 'ae', 'Ä' => 'AE', 'æ' => 'ae', 'Æ' => 'AE', 'ḃ' => 'b', 'Ḃ' => 'B', 'ć' => 'c', 'Ć' => 'C', 'ĉ' => 'c', 'Ĉ' => 'C', 'č' => 'c', 'Č' => 'C', 'ċ' => 'c', 'Ċ' => 'C', 'ç' => 'c', 'Ç' => 'C', 'ď' => 'd', 'Ď' => 'D', 'ḋ' => 'd', 'Ḋ' => 'D', 'đ' => 'd', 'Đ' => 'D', 'ð' => 'dh', 'Ð' => 'Dh', 'é' => 'e', 'É' => 'E', 'è' => 'e', 'È' => 'E', 'ĕ' => 'e', 'Ĕ' => 'E', 'ê' => 'e', 'Ê' => 'E', 'ě' => 'e', 'Ě' => 'E', 'ë' => 'e', 'Ë' => 'E', 'ė' => 'e', 'Ė' => 'E', 'ę' => 'e', 'Ę' => 'E', 'ē' => 'e', 'Ē' => 'E', 'ḟ' => 'f', 'Ḟ' => 'F', 'ƒ' => 'f', 'Ƒ' => 'F', 'ğ' => 'g', 'Ğ' => 'G', 'ĝ' => 'g', 'Ĝ' => 'G', 'ġ' => 'g', 'Ġ' => 'G', 'ģ' => 'g', 'Ģ' => 'G', 'ĥ' => 'h', 'Ĥ' => 'H', 'ħ' => 'h', 'Ħ' => 'H', 'í' => 'i', 'Í' => 'I', 'ì' => 'i', 'Ì' => 'I', 'î' => 'i', 'Î' => 'I', 'ï' => 'i', 'Ï' => 'I', 'ĩ' => 'i', 'Ĩ' => 'I', 'į' => 'i', 'Į' => 'I', 'ī' => 'i', 'Ī' => 'I', 'ĵ' => 'j', 'Ĵ' => 'J', 'ķ' => 'k', 'Ķ' => 'K', 'ĺ' => 'l', 'Ĺ' => 'L', 'ľ' => 'l', 'Ľ' => 'L', 'ļ' => 'l', 'Ļ' => 'L', 'ł' => 'l', 'Ł' => 'L', 'ṁ' => 'm', 'Ṁ' => 'M', 'ń' => 'n', 'Ń' => 'N', 'ň' => 'n', 'Ň' => 'N', 'ñ' => 'n', 'Ñ' => 'N', 'ņ' => 'n', 'Ņ' => 'N', 'ó' => 'o', 'Ó' => 'O', 'ò' => 'o', 'Ò' => 'O', 'ô' => 'o', 'Ô' => 'O', 'ő' => 'o', 'Ő' => 'O', 'õ' => 'o', 'Õ' => 'O', 'ø' => 'oe', 'Ø' => 'OE', 'ō' => 'o', 'Ō' => 'O', 'ơ' => 'o', 'Ơ' => 'O', 'ö' => 'oe', 'Ö' => 'OE', 'ṗ' => 'p', 'Ṗ' => 'P', 'ŕ' => 'r', 'Ŕ' => 'R', 'ř' => 'r', 'Ř' => 'R', 'ŗ' => 'r', 'Ŗ' => 'R', 'ś' => 's', 'Ś' => 'S', 'ŝ' => 's', 'Ŝ' => 'S', 'š' => 's', 'Š' => 'S', 'ṡ' => 's', 'Ṡ' => 'S', 'ş' => 's', 'Ş' => 'S', 'ș' => 's', 'Ș' => 'S', 'ß' => 'SS', 'ť' => 't', 'Ť' => 'T', 'ṫ' => 't', 'Ṫ' => 'T', 'ţ' => 't', 'Ţ' => 'T', 'ț' => 't', 'Ț' => 'T', 'ŧ' => 't', 'Ŧ' => 'T', 'ú' => 'u', 'Ú' => 'U', 'ù' => 'u', 'Ù' => 'U', 'ŭ' => 'u', 'Ŭ' => 'U', 'û' => 'u', 'Û' => 'U', 'ů' => 'u', 'Ů' => 'U', 'ű' => 'u', 'Ű' => 'U', 'ũ' => 'u', 'Ũ' => 'U', 'ų' => 'u', 'Ų' => 'U', 'ū' => 'u', 'Ū' => 'U', 'ư' => 'u', 'Ư' => 'U', 'ü' => 'ue', 'Ü' => 'UE', 'ẃ' => 'w', 'Ẃ' => 'W', 'ẁ' => 'w', 'Ẁ' => 'W', 'ŵ' => 'w', 'Ŵ' => 'W', 'ẅ' => 'w', 'Ẅ' => 'W', 'ý' => 'y', 'Ý' => 'Y', 'ỳ' => 'y', 'Ỳ' => 'Y', 'ŷ' => 'y', 'Ŷ' => 'Y', 'ÿ' => 'y', 'Ÿ' => 'Y', 'ź' => 'z', 'Ź' => 'Z', 'ž' => 'z', 'Ž' => 'Z', 'ż' => 'z', 'Ż' => 'Z', 'þ' => 'th', 'Þ' => 'Th', 'µ' => 'u', 'а' => 'a', 'А' => 'a', 'б' => 'b', 'Б' => 'b', 'в' => 'v', 'В' => 'v', 'г' => 'g', 'Г' => 'g', 'д' => 'd', 'Д' => 'd', 'е' => 'e', 'Е' => 'E', 'ё' => 'e', 'Ё' => 'E', 'ж' => 'zh', 'Ж' => 'zh', 'з' => 'z', 'З' => 'z', 'и' => 'i', 'И' => 'i', 'й' => 'j', 'Й' => 'j', 'к' => 'k', 'К' => 'k', 'л' => 'l', 'Л' => 'l', 'м' => 'm', 'М' => 'm', 'н' => 'n', 'Н' => 'n', 'о' => 'o', 'О' => 'o', 'п' => 'p', 'П' => 'p', 'р' => 'r', 'Р' => 'r', 'с' => 's', 'С' => 's', 'т' => 't', 'Т' => 't', 'у' => 'u', 'У' => 'u', 'ф' => 'f', 'Ф' => 'f', 'х' => 'h', 'Х' => 'h', 'ц' => 'c', 'Ц' => 'c', 'ч' => 'ch', 'Ч' => 'ch', 'ш' => 'sh', 'Ш' => 'sh', 'щ' => 'sch', 'Щ' => 'sch', 'ъ' => '', 'Ъ' => '', 'ы' => 'y', 'Ы' => 'y', 'ь' => '', 'Ь' => '', 'э' => 'e', 'Э' => 'e', 'ю' => 'ju', 'Ю' => 'ju', 'я' => 'ja', 'Я' => 'ja');
    public static $transliterationRegex = '~&([a-z]{1,2})(acute|uml|circ|grave|ring|cedil|slash|tilde|caron|lig|quot|rsquo|orn|th);~i';

    public static function makeNiceUrlSafeString($string, $lower=true, $transliteration=true, $replaceSpace=true)
    {
//********************************************************************
        $string = html_entity_decode($string);

        if($lower){
            $string = strtolower(trim($string));
        }

        if($transliteration){
            $string = preg_replace(ApplicationLibrary::$transliterationRegex, '$1', $string);
            $string = str_replace(array_keys(ApplicationLibrary::$transliterationTable), array_values(ApplicationLibrary::$transliterationTable), $string);    
        }
        
        if($replaceSpace){
            $string = preg_replace('/[\s]/', '-', $string); //vervang whitespace met -
            $string = preg_replace('/(\-\-+)/', '-', $string); //vervang -- met -    
        }

        $string = preg_replace('/[^A-z0-9- ]/', '', $string);
        // $string = urlencode($string);
        return $string;
    }


    public function renderWithCache(string $view, array $parameters = [], Response $response = null): Response
    {
        $content = $this->renderView($view, $parameters);

        $hash = md5(join(array_filter(explode("\n", $content), function($line){
            $ok = true;
            if(str_contains($line, 'token')) $ok = false; //slaat regels met 'token' over in cache hash
            return $ok;
        })));
        
        if (null === $response) {
            $response = new Response();
        }

        $response->setContent($content);

        return $this->contentCachedResponse($response, $hash);
    }

    public function contentCachedResponse(Response $response, string $hash = ''): Response
    {
        if(empty($hash)){
            $hash=md5($response->getContent());
        }

        $response->setEtag($hash);
        $response->setPublic(); // make sure the response is public/cacheable
        $response->isNotModified($this->request);   

        return $response;
    }


//functies uit AbstractController om goede responses terug te geven vanuit ApplicLibrary
/**
 * Returns a rendered view.
 */
    protected function renderView(string $view, array $parameters = []): string
    {
        if (!$this->container->has('twig')) {
            throw new \LogicException('You can not use the "renderView" method if the Twig Bundle is not available. Try running "composer require symfony/twig-bundle".');
        }

        return $this->container->get('twig')->render($view, $parameters);
    }

/**
 * Renders a view.
 */
    public function render(string $view, array $parameters = [], Response $response = null): Response
    {
        $content = $this->renderView($view, $parameters);

        if (null === $response) {
            $response = new Response();
        }

        $response->setContent($content);

        return $response;
    }

/**
 * Creates and returns a form builder instance.
 */
    protected function createFormBuilder($data = null, array $options = []): FormBuilderInterface
    {
        return $this->container->get('form.factory')->createBuilder(FormType::class, $data, $options);
    }
}
