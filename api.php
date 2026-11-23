<?php
/*
Gift of Lights plugin API, under /api/plugin/fpp-plugin-GiftOfLights/ (FPP's plugin endpoint mechanism).

  GET  settings   the website address, on/off, show names, whether a key is saved (never the key itself)
  POST settings   save them; a key is replaced only when one is sent
  GET  status     the sender's last post or error, whether it is running, events waiting
  POST test       queue a test song, so the sender posts it like a real one

Settings go in config/plugin.fpp-plugin-GiftOfLights (WriteSettingToFile); the key goes in plugindata/, never config/.
*/

function fpppluginGiftOfLightsDataDir() {
    global $settings;
    return $settings['mediaDirectory'] . '/plugindata/fpp-plugin-GiftOfLights';
}

function fpppluginGiftOfLightsKeyFile() {
    return fpppluginGiftOfLightsDataDir() . '/key';
}

function getEndpointsfpppluginGiftOfLights() {
    return array(
        array('method' => 'GET', 'endpoint' => 'settings', 'callback' => 'fpppluginGiftOfLightsGetSettings'),
        array('method' => 'POST', 'endpoint' => 'settings', 'callback' => 'fpppluginGiftOfLightsSaveSettings'),
        array('method' => 'GET', 'endpoint' => 'status', 'callback' => 'fpppluginGiftOfLightsStatus'),
        array('method' => 'POST', 'endpoint' => 'test', 'callback' => 'fpppluginGiftOfLightsTest'),
    );
}

function fpppluginGiftOfLightsGetSettings() {
    $key = @file_get_contents(fpppluginGiftOfLightsKeyFile());
    $key = $key === false ? '' : trim($key);
    return json(array(
        'backendUrl' => ReadSettingFromFile('BackendUrl', 'fpp-plugin-GiftOfLights'),
        'enabled' => ReadSettingFromFile('Enabled', 'fpp-plugin-GiftOfLights') !== '0',
        'showNames' => str_replace('|', "\n", ReadSettingFromFile('ShowNames', 'fpp-plugin-GiftOfLights')),
        'keySet' => strlen($key) >= 16,
        'keyEnd' => strlen($key) >= 16 ? substr($key, -4) : '',
    ));
}

function fpppluginGiftOfLightsSaveSettings() {
    $in = json_decode(file_get_contents('php://input'), true);
    if (!is_array($in)) {
        http_response_code(400);
        return json(array('error' => 'Send JSON.'));
    }
    $url = trim(isset($in['backendUrl']) ? $in['backendUrl'] : '');
    if ($url !== '' && !preg_match('#^https://[^\s"|]+$#', $url)) {
        http_response_code(400);
        return json(array('error' => 'The website address must start with https:// .'));
    }
    $names = isset($in['showNames']) ? (string) $in['showNames'] : '';
    $lines = array();
    foreach (preg_split('/\r?\n/', $names) as $line) {
        $line = trim(str_replace(array('|', '"'), '', $line));
        if ($line !== '') {
            $lines[] = substr($line, 0, 200);
        }
    }
    // Everything is checked before anything is written, so a refused save changes nothing.
    $key = isset($in['key']) ? trim((string) $in['key']) : '';
    if ($key !== '' && (strlen($key) < 16 || strlen($key) > 200 || preg_match('/\s/', $key))) {
        http_response_code(400);
        return json(array('error' => 'The key must be 16 to 200 characters with no spaces.'));
    }
    // FPP 10's WriteSettingToFile returns false (and only logs) when it cannot write; say so on the page.
    $cfg = 'plugin.fpp-plugin-GiftOfLights in the config folder';
    foreach (array(
        array('BackendUrl', $url),
        array('Enabled', empty($in['enabled']) ? '0' : '1'),
        array('ShowNames', implode('|', array_slice($lines, 0, 50))),
    ) as $kv) {
        if (WriteSettingToFile($kv[0], $kv[1], 'fpp-plugin-GiftOfLights') === false) {
            http_response_code(500);
            return json(array('error' => 'Not saved: FPP could not write ' . $kv[0] . ' to ' . $cfg . '. See FPP\'s Apache error log.'));
        }
    }
    if ($key !== '') {
        $dir = fpppluginGiftOfLightsDataDir();
        if (!is_dir($dir) && !@mkdir($dir, 0700, true)) {
            http_response_code(500);
            return json(array('error' => 'Not saved: could not make the folder ' . $dir . ' (the web server cannot write there).'));
        }
        $file = fpppluginGiftOfLightsKeyFile();
        if (@file_put_contents($file, $key) === false) {
            http_response_code(500);
            return json(array('error' => 'Not saved: could not write the key to ' . $file . ' (the web server cannot write there).'));
        }
        @chmod($file, 0600);
    }
    return fpppluginGiftOfLightsGetSettings();
}

function fpppluginGiftOfLightsStatus() {
    $dir = fpppluginGiftOfLightsDataDir();
    $status = @json_decode(@file_get_contents($dir . '/status.json'), true);
    $pid = trim((string) @file_get_contents($dir . '/sender.pid'));
    $running = $pid !== '' && ctype_digit($pid) && file_exists('/proc/' . $pid);
    $waiting = count(glob($dir . '/queue/*.json') ?: array());
    return json(array('status' => is_array($status) ? $status : new stdClass(), 'running' => $running, 'waiting' => $waiting));
}

function fpppluginGiftOfLightsTest() {
    $dir = fpppluginGiftOfLightsDataDir() . '/queue';
    if (!is_dir($dir)) {
        @mkdir($dir, 0755, true);
    }
    $ev = array('title' => 'Test song', 'artist' => 'Gift of Lights plugin', 'show' => 'Plugin test', 'queuedAt' => microtime(true));
    $name = sprintf('%020d-test', (int) (microtime(true) * 1000000000));
    $tmp = $dir . '/.' . $name;
    if (file_put_contents($tmp, json_encode($ev)) === false || !rename($tmp, $dir . '/' . $name . '.json')) {
        http_response_code(500);
        return json(array('error' => 'Could not queue the test.'));
    }
    return json(array('queued' => true));
}
?>
