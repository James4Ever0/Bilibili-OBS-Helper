const fs = require("fs");
const path = require("path");

const configPath = path.join(require('os').homedir(), ".config/obs-studio/basic/profiles/Untitled/service.json")

function updateLiveKey(key) {
    const configObj = {
        "settings": {
            "bwtest": false,
            "key": key,
            "server": "rtmp://live-push.bilivideo.com/live-bvc/",
            "use_auth": false
        },
        "type": "rtmp_custom"
    };
    fs.writeFileSync(configPath, JSON.stringify(configObj));
}

module.exports = {
    updateLiveKey,
}