<?php
if (!isset($_SERVER['PHP_AUTH_USER']) || !$_SERVER['PHP_AUTH_USER']) {
	header('WWW-Authenticate: Basic realm="My Realm"');
	header('HTTP/1.0 401 Unauthorized');
	exit;
}
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

$output = null;
if (isset($_GET['output'])) {
	$output = $_GET['output'];
}

$path = '../documents/'.$millesime.'/'.substr($cvi, 0, 2);

switch ($action) {
	case 'scrape':
	case 'update':
		$type = null;
		if (isset($_GET['type'])) {
			$type = $_GET['type'];
		}
		switch ($type) {
			case 'sv11':
			case 'sv12':
			case 'dr':
				exec('DEBUG_WITH_BROWSER=true PRODOUANE_NO_WWWDATA=true bash ../bin/download_douane.sh '.$type.' '.$millesime.' '.$cvi.' 2>&1', $exec_output, $ret);
				if (file_exists($path.'/'.$type.'-'.$millesime.'-'.$cvi.'.pdf') || file_exists('../documents/'.$type.'-'.$millesime.'-'.$cvi.'.pdf')) {
					if ($ret == 0) {
						header('Location: '.str_replace('action='.$action.'&', 'action=list&', $_SERVER['REQUEST_URI']));
					}
				} else {
						header('HTTP/1.0 500 Scraping failed');
						echo "scraping failed : files not found\n";
						$output = 'error';
				}
				if ($output) {
					echo implode("\n", $exec_output);
					echo "\n";
					exit;
				}
				break;
			case 'parcellaire':
				exec('PRODOUANE_NO_WWWDATA=true bash ../bin/download_parcellaire.sh '.$cvi.' 2>&1', $exec_output, $ret);
				if (file_exists($path.'/parcellaire-'.$cvi.'.csv') || file_exists('../documents/parcellaire-'.$cvi.'.csv')) {
					if ($ret == 0) {
						header('Location: '.str_replace('action='.$action.'&', 'action=list&', $_SERVER['REQUEST_URI']));
					}
				} else {
					header('HTTP/1.0 500 Scraping failed');
					echo "scraping failed : files not found\n";
					$output = 'error';
				}
				if ($output) {
					echo implode("\n", $exec_output);
					echo "\n";
					exit;
				}
				break;
			default:
				header('HTTP/1.0 400 Bad Request');
				echo "valeur de type reconnu\n";
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
				header('HTTP/1.0 400 Bad Request');
				echo "argument type nécessaire\n";
				exit;
				break;
		}
		switch ($output) {
			case 'json':
				header('Content-Type: text/json');
				echo json_encode($files);
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
			header('HTTP/1.0 400 Bad Request');
			echo "argument filename nécessaire\n";
			exit;
		}
		$filename = str_replace('/', '', $_GET['filename']);
		$fullpath = $path.'/'.$filename;
		if (!file_exists($fullpath)) {
			$fullpath = '../documents/'.$filename;
			if (!file_exists($fullpath)) {
				header('HTTP/1.0 400 Bad Request');
				echo "wrong file\n";
				exit;
			}
		}
		header('Content-Type: application/download');
		header('Content-Disposition: attachment; filename="'.urlencode($filename).'"');

		echo file_get_contents($fullpath);
		exit;
	default:
		header('HTTP/1.0 400 Bad Request');
		echo "action inconnue\n";
		exit;
		break;
}
