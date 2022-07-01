const express = require('express')
const _ = require("lodash")
const app = express()
const port = 3000

const { fetchLiveKey } = require("./bilibili")

app.get('/', (req, res) => {
    res.send('Hello World!')
})

async function handler(req, res) {
    let liveKey = "";
    try {
        liveKey = await fetchLiveKey();
    } catch (err) {
        console.error(err)
    }
    res.json({
        success: 1,
        key: liveKey,
    });
}

app.get('/key', _.debounce(handler, 5 * 1000, {
    leading: true,
}));

app.listen(port, () => {
    console.log(`Example app listening on port ${port}`)
})