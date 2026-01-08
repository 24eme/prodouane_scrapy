<?php
include('../bin/config.php');

const SCRAPING_FILE_NOT_FOUND = 666;
const SCRAPING_NO_CONF_FOUND = 888;
const SCRAPING_UNKOWN_TYPE = 999;
const SCRAPING_JSON_NATIF = 750;

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
	$format = preg_replace('/[^0-9a-z]/', '', $_GET['format']);
}

$type = null;
if (isset($_GET['type'])) {
	$type = $_GET['type'];
	if (!in_array($type, ['parcellaire', 'dr', 'sv11', 'sv12', 'production', 'verify', 'cvi'])) {
		$type = null;
	}
}

$dep = substr($cvi, 0, 2);
$path = '../documents/'.$millesime.'/'.$dep;
@mkdir('../documents/'.$millesime);
@mkdir('../documents/'.$millesime.'/'.$dep);
api_log($type, $millesime, $cvi, ['api: '.$account_name.': action '.$action]);

switch ($action) {
	case 'scrape':
	case 'update':
	case 'verify':
		$type = null;
		if (isset($_GET['type'])) {
			$type = $_GET['type'];
		}
		$ret = parsing($account_name, $type, $millesime, $cvi, $exec_output);
		api_log($type, $millesime, $cvi, ['parsing DONE']);
		if ($format) {
			api_log($type, $millesime, $cvi, ['response format: '.$format]);
		}
		$json_message = [];
		switch ($ret) {
			case 0:
				if ($format != 'json') {
					api_log($type, $millesime, $cvi, ['redirect to list']);
					header('Location: '.str_replace('action='.$action.'&', 'action=list&', $_SERVER['REQUEST_URI']));
				}
				break;
			case SCRAPING_JSON_NATIF:
				if ($format == 'json') {
					echo implode("\n", $exec_output);
					echo "\n";
					exit;
				}
				break;
			case SCRAPING_UNKOWN_TYPE:
				if ($format != 'json') {
					api_log($type, $millesime, $cvi, ['HTTP 400 Bad Request']);
					header('HTTP/1.0 400 Bad Request');
				}
				echo json_encode(['error_code' => $ret, 'msg' => 'valeur de type non reconnu'])."\n";
				api_log($type, $millesime, $cvi, ['valeur de type non reconnu']);
				exit;
			case SCRAPING_NO_CONF_FOUND:
				if ($format != 'json') {
					api_log($type, $millesime, $cvi, ['HTTP 400 Bad Request']);
					header('HTTP/1.0 400 Bad Request');
				}
				echo json_encode(['error_code' => $ret, 'msg' => 'no conf found'])."\n";
				api_log($type, $millesime, $cvi, ['no conf found']);
				exit;
			case SCRAPING_FILE_NOT_FOUND:
				if ($format != 'json') {
					header('HTTP/1.0 500 Scraping failed');
					api_log($type, $millesime, $cvi, ['HTTP 500 Scraping failed']);
				}
				$json_message['msg'] = "scraping failed : files not found";
				api_log($type, $millesime, $cvi, ['files not found']);
				$format = 'error';
				break;
			default:
				if ($format != 'json') {
					header('HTTP/1.0 500 Scraping failed');
					api_log($type, $millesime, $cvi, ['HTTP 500 Scraping failed']);
				}
				$json_message['msg'] =  "scraping failed : error $ret";
				api_log($type, $millesime, $cvi, ["scraping failed : error $ret"]);
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
		$files = [$type.'-'.$millesime.'-'.$cvi.'.log'];
		switch ($type) {
			case 'sv11':
			case 'sv12':
			case 'dr':
			case 'production':
				$filetype = $type;
				if ($millesime > 2021 && ($type == 'sv11' || $type == 'sv12')) {
					$filetype = 'production';
				}elseif ($millesime > 2024 && $type == 'dr') {
					$filetype = 'recolte';
				}
				if (file_exists($path.'/'.$filetype.'-'.$millesime.'-'.$cvi.'.pdf') || file_exists('../documents/'.$filetype.'-'.$millesime.'-'.$cvi.'.pdf')) {
					$files[] = $filetype.'-'.$millesime.'-'.$cvi.'.pdf';
				}
				if (file_exists($path.'/'.$filetype.'-'.$millesime.'-'.$cvi.'.xls') || file_exists('../documents/'.$filetype.'-'.$millesime.'-'.$cvi.'.xls')) {
					$files[] = $filetype.'-'.$millesime.'-'.$cvi.'.xls';
				}
				if (file_exists($path.'/'.$filetype.'-'.$millesime.'-'.$cvi.'.xlsx') || file_exists('../documents/'.$filetype.'-'.$millesime.'-'.$cvi.'.xlsx')) {
					$files[] = $filetype.'-'.$millesime.'-'.$cvi.'.xlsx';
				}
				if (file_exists($path.'/'.$filetype.'-'.$millesime.'-'.$cvi.'.csv') || file_exists('../documents/'.$filetype.'-'.$millesime.'-'.$cvi.'.csv')) {
					$files[] = $filetype.'-'.$millesime.'-'.$cvi.'.csv';
				}
				if (file_exists($path.'/'.$filetype.'-'.$millesime.'-'.$cvi.'.html') || file_exists('../documents/'.$filetype.'-'.$millesime.'-'.$cvi.'.html')) {
					$files[] = $filetype.'-'.$millesime.'-'.$cvi.'.html';
				}
				if (file_exists($path.'/'.$filetype.'-'.$millesime.'-'.$cvi.'.json') || file_exists('../documents/'.$filetype.'-'.$millesime.'-'.$cvi.'.json')) {
					$files[] = $filetype.'-'.$millesime.'-'.$cvi.'.json';
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
					api_log($type, $millesime, $cvi, ['HTTP/1.0 400 Bad Request']);
				}
				echo json_encode(['error_code' => '400', 'msg' => 'argument type nécessaire'])."\n";
				api_log($type, $millesime, $cvi, ['unknown type '.$_GET['type']]);
				exit;
				break;
		}
		api_log($type, $millesime, $cvi, ['files found: '.implode(', ', $files)]);
		switch ($format) {
			case 'json':
				api_log($type, $millesime, $cvi, ['json response']);
				header('Content-Type: text/json');
				echo json_encode(['files' => $files]);
				echo "\n";
				break;
			default:
				header('Content-Type: text/json');
				api_log($type, $millesime, $cvi, ['listing response']);
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
				api_log($type, $millesime, $cvi, ['HTTP 400 Bad Request']);
			}
			echo json_encode(['error_code' => '400', 'msg' => 'argument filename nécessaire'])."\n";
			api_log($type, $millesime, $cvi, ['argument filename nécessaire']);
			exit;
		}
		$filename = str_replace('/', '', $_GET['filename']);
		if (! strpos($filename, $cvi)) {
			if ($format != 'json') {
				header('HTTP/1.0 400 Bad Request');
				api_log($type, $millesime, $cvi, ['HTTP 400 Bad Request']);
			}
			echo json_encode(['error_code' => '400', 'msg' => 'wrong filename'])."\n";
			api_log($type, $millesime, $cvi, ['wrong filename']);
			exit;
		}
		$fullpath = $path.'/'.$filename;
		$files = [];
		if (file_exists($fullpath)) {
			$files[] = $fullpath;
		}
		if (file_exists('../documents/'.$filename)) {
			$files[] = '../documents/'.$filename;
		}
		if (count($files) < 1) {
			if ($format != 'json') {
				header('HTTP/1.0 400 Bad Request');
				api_log($type, $millesime, $cvi, ['HTTP 400 Bad Request']);
			}
			echo json_encode(['error_code' => '400', 'msg' => 'wrong file'])."\n";
			api_log($type, $millesime, $cvi, ['wrong file']);
			exit;
		}
		if (count($files) == 1)  {
			$fullpath = $files[0];
		} else {
			if (filemtime($files[0]) < filemtime($files[1])) {
				$fullpath = $files[1];
				unlink($files[0]);
			} else {
				$fullpath = $files[0];
				unlink($files[1]);
			}
		}
		api_log($type, $millesime, $cvi, [$filename.' sent']);
		if (strpos($filename, '.log') === false) {
			header('Content-Type: application/download');
			header('Content-Disposition: attachment; filename="'.urlencode($filename).'"');
		}else{
			header('Content-Type: text/plain');
		}
		echo file_get_contents($fullpath);
		exit;
	default:
		if ($format != 'json') {
			header('HTTP/1.0 400 Bad Request');
			api_log($type, $millesime, $cvi, ['HTTP 400 Bad Request']);
		}
		echo json_encode(['error_code' => '400', 'msg' => 'action inconnue'])."\n";
		api_log($type, $millesime, $cvi, ['action inconnue']);
		echo "action inconnue\n";
		exit;
		break;
}

function parsing($acccount_name, $type, $millesime, $cvi, &$exec_output) {
	$ret = exec_local_parsing($acccount_name, $type, $millesime, $cvi, $exec_output);
	if (!$ret) {
		return $ret;
	}
	if ($ret == SCRAPING_JSON_NATIF) {
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

	api_log($type, $millesime, $cvi, ['api: '.$config_name.': local_parsing']);
	if (isset($config_script_prefix) && $config_script_prefix) {
		$script_prefix = $config_script_prefix;
	}else{
		$script_prefix = '';
	}
	if (file_exists('../bin/config.'.$config_name.'.inc')) {
		api_log($type, $millesime, $cvi, ['exec_local_parsing: '.$config_name.': config: '.'config.'.$config_name.'.inc']);
		$script_prefix .= ' PRODOUANE_CONFIG_FILENAME=config.'.$config_name.'.inc';
	}elseif (!file_exists('../bin/config.inc')) {
		api_log($type, $millesime, $cvi, ['exec_local_parsing: '.$config_name.': config: not found']);
		return SCRAPING_NO_CONF_FOUND;
	}else{
		api_log($type, $millesime, $cvi, ['exec_local_parsing: '.$config_name.': config: '.'config.inc']);
	}
	switch ($type) {
		case 'sv11':
		case 'sv12':
		case 'dr':
			api_log($type, $millesime, $cvi, ['exec_local_parsing: '.$config_name.': exec: '.$script_prefix.' bash ../bin/download_douane.sh '.$type.' '.$millesime.' '.$cvi.' 2>&1']);
			exec($script_prefix.' bash ../bin/download_douane.sh '.$type.' '.$millesime.' '.$cvi.' 2>&1', $exec_output, $ret);
			api_log($type, $millesime, $cvi, ['===============================================']);
			api_log($type, $millesime, $cvi, $exec_output);
			api_log($type, $millesime, $cvi, ['===============================================']);
			api_log($type, $millesime, $cvi, ['exec_local_parsing: '.$config_name.': exec: ret: '.$ret]);
			if ($ret) {
				return $ret;
			}
			$filetype = $type;
			if ($millesime > 2021 && ($type == 'sv11' || $type == 'sv12')) {
				$filetype = 'production';
			}
			if ($millesime > 2024 && $type == 'dr') {
				$filetype = 'recolte';
			}
			if (file_exists($path.'/'.$filetype.'-'.$millesime.'-'.$cvi.'.pdf') || file_exists('../documents/'.$filetype.'-'.$millesime.'-'.$cvi.'.pdf')) {
				api_log($type, $millesime, $cvi, ['exec_local_parsing: '.$config_name.': exec: pdf file exists']);
				return 0;
			}
			api_log($type, $millesime, $cvi, ['exec_local_parsing: '.$config_name.': exec: SCRAPING_FILE_NOT_FOUND']);
			return SCRAPING_FILE_NOT_FOUND;
		case 'verify':
		case 'cvi':
			api_log($type, $millesime, $cvi, ['exec_local_parsing: '.$config_name.': exec: '.$script_prefix.' bash ../bin/verify_cvi.sh '.$cvi.' 2>&1']);
			exec($script_prefix.' bash ../bin/verify_cvi.sh '.$cvi.' 2>&1', $exec_output, $ret);
			if (count($exec_output)) {
				api_log($type, $millesime, $cvi, ['===============================================']);
				api_log($type, $millesime, $cvi, $exec_output);
				api_log($type, $millesime, $cvi, ['===============================================']);
			}
			if (!$ret) {
				return SCRAPING_JSON_NATIF;
			}
			return $ret;
		case 'parcellaire':
			api_log($type, $millesime, $cvi, ['exec_local_parsing: '.$config_name.': exec: '.$script_prefix.' bash ../bin/download_parcellaire.sh '.$cvi.' 2>&1']);
			exec($script_prefix.' bash ../bin/download_parcellaire.sh '.$cvi.' 2>&1', $exec_output, $ret);
			if (count($exec_output)) {
				api_log($type, $millesime, $cvi, ['===============================================']);
				api_log($type, $millesime, $cvi, $exec_output);
				api_log($type, $millesime, $cvi, ['===============================================']);
			}
			api_log($type, $millesime, $cvi, ['exec_local_parsing: '.$config_name.': exec: ret: '.$ret]);
			if ($ret) {
				return $ret;
			}
			if (!file_exists($path.'/parcellaire-'.$cvi.'.csv') && !file_exists('../documents/parcellaire-'.$cvi.'.csv')) {
				api_log($type, $millesime, $cvi, ['exec_local_parsing: '.$config_name.': exec: pdf file exists']);
				return SCRAPING_FILE_NOT_FOUND;
			}
			api_log($type, $millesime, $cvi, ['exec_local_parsing: '.$config_name.': exec: '.$script_prefix.' bash ../bin/download_parcellaire_geojson.sh '.$cvi.' 2>&1']);
			exec($script_prefix.' bash ../bin/download_parcellaire_geojson.sh '.$cvi.' 2>&1', $exec_output, $ret);
			if (count($exec_output)) {
				api_log($type, $millesime, $cvi, ['===============================================']);
				api_log($type, $millesime, $cvi, $exec_output);
				api_log($type, $millesime, $cvi, ['===============================================']);
			}
			api_log($type, $millesime, $cvi, ['exec_local_parsing: '.$config_name.': exec: ret: '.$ret]);
			if ($ret) {
				return $ret;
			}
			api_log($type, $millesime, $cvi, ['exec_local_parsing: '.$config_name.': exec: ret: return 0']);
			return 0;
	}
	api_log($type, $millesime, $cvi, ['exec_local_parsing: '.$config_name.': exec: SCRAPING_UNKOWN_TYPE']);
	return SCRAPING_UNKOWN_TYPE;
}

function exec_distant_parsing($config_name, $type, $millesime, $cvi, & $exec_output) {
	global $config_router_uri;
	$dep = substr($cvi, 0, 2);

	api_log($type, $millesime, $cvi, ['exec_distant_parsing: '.$config_name.': distant_parsing']);
	$router_uri = str_replace('://', '://'.$_SERVER['PHP_AUTH_USER'].':'.$_SERVER['PHP_AUTH_PW'].'@', $config_router_uri);

	api_log($type, $millesime, $cvi, ['exec_distant_parsing: '.$config_name.': distant_parsing '.$config_router_uri.': list']);
	api_log($type, $millesime, $cvi, ['exec_distant_parsing: '.$config_name.': distant_parsing '.$config_router_uri.': /router.php?action=list&type='.$type.'&millesime='.$millesime.'&cvi='.$cvi]);
	$response = file_get_contents($router_uri.'/router.php?action=list&type='.$type.'&millesime='.$millesime.'&cvi='.$cvi);
	api_log($type, $millesime, $cvi, ['exec_distant_parsing: '.$config_name.': distant_parsing '.$config_router_uri.': list response: '.$response]);
	$json = json_decode($response);
	if (isset($json->error_code) || (isset($json->files) && count($json->files) < 2) ) {
		api_log($type, $millesime, $cvi, ['exec_distant_parsing: '.$config_name.': distant_parsing '.$config_router_uri.': update']);
		api_log($type, $millesime, $cvi, ['exec_distant_parsing: '.$config_name.': distant_parsing '.$config_router_uri.': /router.php?action=update&type='.$type.'&millesime='.$millesime.'&cvi='.$cvi]);
		$response = file_get_contents($router_uri.'/router.php?action=update&type='.$type.'&millesime='.$millesime.'&cvi='.$cvi);
		$json = json_decode($response);
		if (isset($json->via)) {
			api_log($type, $millesime, $cvi, ['exec_distant_parsing: '.$config_name.': distant_parsing '.$config_router_uri.': update via: '.implode(',', $json->via)]);
		}
		if (isset($json->exec_output)) {
			api_log($type, $millesime, $cvi, ['exec_distant_parsing: '.$config_name.': distant_parsing '.$config_router_uri.': exec_output: ']);
			api_log($type, $millesime, $cvi, ['===============================================']);
			$exec_output = $json->exec_output;
			api_log($type, $millesime, $cvi, $exec_output, $config_router_uri);
			api_log($type, $millesime, $cvi, ['===============================================']);
		}
		if (isset($json->error_code)) {
			api_log($type, $millesime, $cvi, ['exec_distant_parsing: '.$config_name.': distant_parsing '.$config_router_uri.': error_code:'.$json->error_code]);
		}
		if (isset($json->error_code) && !$json->error_code) {
			api_log($type, $millesime, $cvi, ['exec_distant_parsing: '.$config_name.': distant_parsing '.$config_router_uri.': listing']);
			api_log($type, $millesime, $cvi, ['exec_distant_parsing: '.$config_name.': distant_parsing '.$config_router_uri.': /router.php?action=list&type='.$type.'&millesime='.$millesime.'&cvi='.$cvi]);
			$response = file_get_contents($router_uri.'/router.php?action=list&type='.$type.'&millesime='.$millesime.'&cvi='.$cvi);
			api_log($type, $millesime, $cvi, ['exec_distant_parsing: '.$config_name.': distant_parsing '.$config_router_uri.': listing response: '.$response]);
			$json = json_decode($response);
			if (isset($json->via)) {
				api_log($type, $millesime, $cvi, ['exec_distant_parsing: '.$config_name.': distant_parsing '.$config_router_uri.': listing via: '.implode(',', $json->via)]);
			}
		}
	}
	if (isset($json->error_code)) {
		api_log($type, $millesime, $cvi, ['exec_distant_parsing: '.$config_name.': distant_parsing '.$config_router_uri.': return error_code'.$json->error_code]);
		return $json->error_code;
	}
	if (!isset($json->files)) {
		api_log($type, $millesime, $cvi, ['exec_distant_parsing: '.$config_name.': distant_parsing '.$config_router_uri.': return response '.$response]);
		return $response;
	}
	foreach($json->files as $f) {
		if (strpos($f, '.pdf') === false && strpos($f, '.csv') === false && strpos($f, '.html') === false  && strpos($f, '.xls') === false && strpos($f, '.xlsx') === false && strpos($f, '.json') === false  && strpos($f, '.geojson') === false && strpos($f, '.log') === false) {
			continue;
		}
		api_log($type, $millesime, $cvi, ['api: '.$config_name.': distant_parsing: file '.$f]);
		if (strpos($f, '.log') !== false) {
			continue;
		}
		api_log($type, $millesime, $cvi, ['exec_distant_parsing: '.$config_name.': distant_parsing '.$config_router_uri.': file']);
		api_log($type, $millesime, $cvi, ['exec_distant_parsing: '.$config_name.': distant_parsing '.$config_router_uri.': /router.php?action=file&type='.$type.'&millesime='.$millesime.'&cvi='.$cvi.'&filename='.$f]);
		$file = file_get_contents($router_uri.'/router.php?action=file&type='.$type.'&millesime='.$millesime.'&cvi='.$cvi.'&filename='.$f);
		file_put_contents('../documents/'.$millesime.'/'.$dep.'/'.$f, $file);
	}
	api_log($type, $millesime, $cvi, ['exec_distant_parsing: '.$config_name.': distant_parsing '.$config_router_uri.': return 0']);
	return 0;
}

function api_log($type, $millesime, $cvi, array $output, $add_prefix = null) {
	$dep = substr($cvi, 0, 2);
	$file = '../documents/'.$millesime.'/'.$dep.'/'.$type.'-'.$millesime.'-'.$cvi.'.log';
	$prefix = date("Y-m-d H:i:s").' '.$_SERVER['REMOTE_ADDR'].' ['.$_SERVER['PHP_AUTH_USER'].']';
	if ($add_prefix) {
		$prefix .= ' '.$add_prefix;
	}
	foreach ($output as $line) {
		error_log($prefix.': '.$line);
		if ($type) {
			file_put_contents($file, $prefix.' '.$line."\n", FILE_APPEND);
		}
	}
}
