<?php
include('../bin/config.php');

const SCRAPING_FILE_NOT_FOUND = 666;
const SCRAPING_NO_CONF_FOUND = 888;
const SCRAPING_UNKOWN_TYPE = 999;

if (!isset($_SERVER['PHP_AUTH_USER']) || !$_SERVER['PHP_AUTH_USER'] || (strpos($_SERVER['REMOTE_ADDR'], '10.20') === false && strpos($_SERVER['REMOTE_ADDR'], '127.') === false && strpos($_SERVER['REMOTE_ADDR'], '::1') === false) ) {
	header('WWW-Authenticate: Basic realm="My Realm"');
	header('HTTP/1.0 401 Unauthorized');
	exit;
}
$account_name = $_SERVER['PHP_AUTH_USER'];
if (!isset($_GET['action'])) {
	header('HTTP/1.0 400 Bad Request');
	echo "argument action nécessaire\n";
	exit;
}
$action = $_GET['action'];

if (!isset($_GET['cvi'])) {
	header('HTTP/1.0 400 Bad Request');
	echo "argument cvi nécessaire\n";
	exit;
}

$cvi = $_GET['cvi'];
$cvi = preg_replace('/[^0-9A-Z]/', '', $cvi);

$millesime = date('Y');
if (isset($_GET['millesime'])) {
	$millesime = substr(preg_replace('/[^0-9]/', '', $_GET['millesime']), 0, 4);
}

$format = null;
if (isset($_GET['format'])) {
	$format = $_GET['format'];
}

$path = '../documents/'.$millesime.'/'.substr($cvi, 0, 2);
error_log('api: '.$account_name.': action '.$action);
switch ($action) {
	case 'scrape':
	case 'update':
		$type = null;
		if (isset($_GET['type'])) {
			$type = $_GET['type'];
		}
		$ret = parsing($account_name, $type, $millesime, $cvi, $exec_output);
		$json_message = [];
		switch ($ret) {
			case 0:
				if ($format != 'json') {
					header('Location: '.str_replace('action='.$action.'&', 'action=list&', $_SERVER['REQUEST_URI']));
				}
				break;
			case SCRAPING_UNKOWN_TYPE:
				if ($format != 'json') {
					header('HTTP/1.0 400 Bad Request');
				}
				echo json_encode(['error_code' => $ret, 'msg' => 'valeur de type reconnu'])."\n";
				exit;
			case SCRAPING_NO_CONF_FOUND:
				if ($format != 'json') {
					header('HTTP/1.0 400 Bad Request');
				}
				echo json_encode(['error_code' => $ret, 'msg' => 'no conf found'])."\n";
				exit;
			case SCRAPING_FILE_NOT_FOUND:
				if ($format != 'json') {
					header('HTTP/1.0 500 Scraping failed');
				}
				$json_message['msg'] = "scraping failed : files not found";
				$format = 'error';
				break;
			default:
				if ($format != 'json') {
					header('HTTP/1.0 500 Scraping failed');
				}
				$json_message['msg'] =  "scraping failed : error $ret";
				$format = 'error';
				break;
		}
		if ($format) {
			$json_message['error_code'] = $ret;
			$json_message['exec_output'] = $exec_output;
			echo json_encode($json_message);
			echo "\n";
			exit;
		}
	case 'list':
		$type = null;
		if (isset($_GET['type'])) {
			$type = $_GET['type'];
		}
		$files = [];
		switch ($type) {
			case 'sv11':
			case 'sv12':
			case 'dr':
				if ($millesime > 2021 && ($type == 'sv11' || $type == 'sv12')) {
					$type = 'production';
				}
				if (file_exists($path.'/'.$type.'-'.$millesime.'-'.$cvi.'.pdf') || file_exists('../documents/'.$type.'-'.$millesime.'-'.$cvi.'.pdf')) {
					$files[] = $type.'-'.$millesime.'-'.$cvi.'.pdf';
				}
				if (file_exists($path.'/'.$type.'-'.$millesime.'-'.$cvi.'.xls') || file_exists('../documents/'.$type.'-'.$millesime.'-'.$cvi.'.xls')) {
					$files[] = $type.'-'.$millesime.'-'.$cvi.'.xls';
				}
				if (file_exists($path.'/'.$type.'-'.$millesime.'-'.$cvi.'.html') || file_exists('../documents/'.$type.'-'.$millesime.'-'.$cvi.'.html')) {
					$files[] = $type.'-'.$millesime.'-'.$cvi.'.html';
				}
				break;
			case 'parcellaire':
				if (file_exists($path.'/parcellaire-'.$cvi.'-accueil.html') || file_exists('../documents/parcellaire-'.$cvi.'-accueil.html')) {
					$files[] = 'parcellaire-'.$cvi.'-accueil.html';
				}
				if (file_exists($path.'/parcellaire-'.$cvi.'.csv') || file_exists('../documents/parcellaire-'.$cvi.'.csv')) {
					$files[] = 'parcellaire-'.$cvi.'.csv';
				}
				if (file_exists($path.'/parcellaire-'.$cvi.'-parcellaire.html') || file_exists('../documents/parcellaire-'.$cvi.'-parcellaire.html')) {
					$files[] = 'parcellaire-'.$cvi.'-parcellaire.html';
				}
				if (file_exists($path.'/parcellaire-'.$cvi.'-parcellaire.pdf') || file_exists('../documents/parcellaire-'.$cvi.'-parcellaire.pdf')) {
					$files[] = 'parcellaire-'.$cvi.'-parcellaire.pdf';
				}
				if (file_exists($path.'/cadastre-'.$cvi.'-parcelles.json') || file_exists('../documents/cadastre-'.$cvi.'-parcelles.json')) {
					$files[] = 'cadastre-'.$cvi.'-parcelles.json';
				}
				break;
			default:
				if ($format != 'json') {
					header('HTTP/1.0 400 Bad Request');
				}
				echo json_encode(['error_code' => '400', 'msg' => 'argument type nécessaire'])."\n";
				exit;
				break;
		}
		switch ($format) {
			case 'json':
				header('Content-Type: text/json');
				echo json_encode(['files' => $files]);
				echo "\n";
				break;
			default:
				header('Content-Type: text/json');
				$protocol = (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS']) ? 'https' : 'http';
				$auth = $_SERVER['PHP_AUTH_USER'].':'.$_SERVER['PHP_AUTH_PW'].'@';
				foreach($files as $f) {
					echo $protocol.'://'.$auth.$_SERVER['HTTP_HOST'].str_replace('action='.$action.'&', 'action=file&', $_SERVER['REQUEST_URI']).'&filename='.urlencode($f)."\n";
				}
				break;
		}
		exit;
	case 'file':
		if (!isset($_GET['filename'])){
			if ($format != 'json') {
				header('HTTP/1.0 400 Bad Request');
			}
			echo json_encode(['error_code' => '400', 'msg' => 'argument filename nécessaire'])."\n";
			exit;
		}
		$filename = str_replace('/', '', $_GET['filename']);
		$fullpath = $path.'/'.$filename;
		if (!file_exists($fullpath)) {
			$fullpath = '../documents/'.$filename;
			if (!file_exists($fullpath)) {
				if ($format != 'json') {
					header('HTTP/1.0 400 Bad Request');
				}
				echo json_encode(['error_code' => '400', 'msg' => 'wrong file'])."\n";
				exit;
			}
		}
		header('Content-Type: application/download');
		header('Content-Disposition: attachment; filename="'.urlencode($filename).'"');

		echo file_get_contents($fullpath);
		exit;
	default:
		if ($format != 'json') {
			header('HTTP/1.0 400 Bad Request');
		}
		echo json_encode(['error_code' => '400', 'msg' => 'action inconnue'])."\n";
		echo "action inconnue\n";
		exit;
		break;
}

function parsing($acccount_name, $type, $millesime, $cvi, &$exec_output) {
	$ret = exec_local_parsing($acccount_name, $type, $millesime, $cvi, $exec_output);
	if (!$ret) {
		return $ret;
	}
	if (!isset($_GET['localonly']) || !$_GET['localonly']) {
		$ret = exec_distant_parsing($acccount_name, $type, $millesime, $cvi, $exec_output);
	}
	return $ret;
}

function exec_local_parsing($config_name, $type, $millesime, $cvi, & $exec_output) {
	global $config_script_prefix;
	global $path;

	error_log('api: '.$config_name.': local_parsing');
	if (isset($config_script_prefix) && $config_script_prefix) {
		$script_prefix = $config_script_prefix;
	}else{
		$script_prefix = '';
	}
	if (file_exists('../bin/config.'.$config_name.'.inc')) {
		error_log('api: '.$config_name.': config: '.'config.'.$config_name.'.inc');
		$script_prefix .= ' PRODOUANE_CONFIG_FILENAME=config.'.$config_name.'.inc';
	}elseif (!file_exists('../bin/config.inc')) {
		error_log('api: '.$config_name.': config: not found');
		return SCRAPING_NO_CONF_FOUND;
	}else{
		error_log('api: '.$config_name.': config: '.'config.inc');
	}
	switch ($type) {
		case 'sv11':
		case 'sv12':
		case 'dr':
			exec($script_prefix.' bash ../bin/download_douane.sh '.$type.' '.$millesime.' '.$cvi.' 2>&1', $exec_output, $ret);
			if ($ret) {
				return $ret;
			}
			if (file_exists($path.'/'.$type.'-'.$millesime.'-'.$cvi.'.pdf') || file_exists('../documents/'.$type.'-'.$millesime.'-'.$cvi.'.pdf')) {
				return 0;
			}
			return SCRAPING_FILE_NOT_FOUND;
		case 'parcellaire':
			exec($script_prefix.' bash ../bin/download_parcellaire.sh '.$cvi.' 2>&1', $exec_output, $ret);
			if ($ret) {
				return $ret;
			}
			if (file_exists($path.'/parcellaire-'.$cvi.'.csv') || file_exists('../documents/parcellaire-'.$cvi.'.csv')) {
				return 0;
			}
			return SCRAPING_FILE_NOT_FOUND;
	}
	return SCRAPING_UNKOWN_TYPE;
}

function exec_distant_parsing($config_name, $type, $millesime, $cvi, & $exec_output) {
	global $config_router_uri;
	$dep = substr($cvi, 0, 2);

	error_log('api: '.$config_name.': distant_parsing');
	$router_uri = str_replace('://', '://'.$_SERVER['PHP_AUTH_USER'].':'.$_SERVER['PHP_AUTH_PW'].'@', $config_router_uri);

	error_log('api: '.$config_name.': distant_parsing: list');
	$response = file_get_contents($router_uri.'/router.php?action=list&type='.$type.'&millesime='.$millesime.'&cvi='.$cvi);
	$json = json_decode($response);
	if (isset($json->error_code) || (isset($json->files) && !count($json->files)) ) {
		error_log('api: '.$config_name.': distant_parsing: update');
		$response = file_get_contents($router_uri.'/router.php?action=update&type='.$type.'&millesime='.$millesime.'&cvi='.$cvi);
		$json = json_decode($response);
		if (isset($json->error_code) && !$json->error_code) {
			$response = file_get_contents($router_uri.'/router.php?action=list&type='.$type.'&millesime='.$millesime.'&cvi='.$cvi);
			$json = json_decode($response);
		}
	}
	if (isset($json->exec_output)) {
		$exec_output = $json->exec_output;
	}
	if (isset($json->error_code)) {
		return $json->error_code;
	}
	if (!isset($json->files)) {
		return $response;
	}
	@mkdir('../documents/'.$millesime);
	@mkdir('../documents/'.$millesime.'/'.$dep);
	foreach($json->files as $f) {
		if (strpos($f, '.pdf') === false && strpos($f, '.csv') === false && strpos($f, '.html') === false  && strpos($f, '.xls') === false && strpos($f, '.xlsx') === false && strpos($f, '.json') === false  && strpos($f, '.geojson') === false) {
			continue;
		}
		error_log('api: '.$config_name.': distant_parsing: file '.$f);
		$file = file_get_contents($router_uri.'/router.php?action=file&type='.$type.'&millesime='.$millesime.'&cvi='.$cvi.'&filename='.$f);
		file_put_contents('../documents/'.$millesime.'/'.$dep.'/'.$f, $file);
	}
	return 0;
}
