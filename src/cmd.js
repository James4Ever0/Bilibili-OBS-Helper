const { fetchLiveKey } = require("./bilibili");
// const { updateLiveKey } = require("./update-obs-config");

(async function run() {
    const key = await fetchLiveKey();
    console.log(key);
    // if (key) {
    //     updateLiveKey(key);
    // }
})();
