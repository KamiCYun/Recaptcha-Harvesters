const electron = require('electron')
const {
    BrowserView,
    app,
    BrowserWindow,
    protocol,
    net,
    ipcMain,
    session,
	globalShortcut 
} = electron;
const fs = require('fs');
const path = require('path');
var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;

site = 'http://recaptcha-demo.appspot.com/recaptcha-v2-checkbox-explicit.php'
sitename = 'google'
sitekey = '6LfW6wATAAAAAHLqO2pb8bDBahxlMxNdo9g947u9'
globalproxy = "localhost"


app.on('ready', () => {
	// globalShortcut.register('Control+Shift+I', () => {
    //     return false;
    // });
    initCaptchaWindow();
})

async function initCaptchaWindow() {

    captchaWindow = new BrowserWindow({
        width: 480,
        height: 680,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
        }
    })
    const view = new BrowserView()
    captchaWindow.setBrowserView(view)
	captchaWindow.setMenuBarVisibility(false)
	captchaWindow.setResizable(false)
    const code = fs.readFileSync(path.join(__dirname, "stealthinject.js"));
    captchaWindow.webContents.on("did-finish-load", () => {
        captchaWindow.webContents.executeJavaScript(code.toString())
      });

    captchaWindow.webContents.session.clearStorageData([], (data) => {})

    captchaWindow.webContents.setUserAgent("Chrome")

    SetupIntercept();

    captchaWindow.loadURL(site);

    captchaWindow.webContents.session.webRequest.onBeforeRequest({
        urls: ['https://myaccount.google.com/*']
    }, (details, callback) => {
        captchaWindow.loadURL(site);
    })


};


ipcMain.on('synchronous-message', (event, arg) => {
    if (arg[0] === "login") {
        captchaWindow.loadURL("https://accounts.google.com/ServiceLogin")
        event.returnValue = ''
    } else if (arg[0] === "proxy") {
        proxy = arg[1]
		globalproxy = proxy
        splitproxy = proxy.split(":")
        if (splitproxy.length == 3) {
            proxy = 'http://' + splitproxy[2] + ":" + splitproxy[3] + "@" + splitproxy[0] + ":" + splitproxy[1]
        } else {
            proxy = 'http://' + splitproxy[0] + ":" + splitproxy[1]
        }
        captchaWindow.webContents.session.setProxy({
            proxyRules: proxy
        }, function() {});
        captchaWindow.webContents.session.clearStorageData([], (data) => {})
        event.returnValue = ''
    } else if (arg[0] === "getprox") {
        event.returnValue = globalproxy
    } else if (arg[0] === "token") {
		token = arg[1]
		var xhr = new XMLHttpRequest();
		xhr.open("POST", 'http://127.0.0.1:5000/recaptcha/add', true);
		xhr.send(JSON.stringify({"token":token,"site":sitename, "version":"v2"}));
		event.returnValue = ""
	}

})

function SetupIntercept() {
    protocol.interceptBufferProtocol('http', (req, callback) => {
        if (req.url == site) {
            fs.readFile(__dirname + '/captcha.html', 'utf8', function(err, html) {
                callback({
                    mimeType: 'text/html',
                    data: Buffer.from(html.replace(/sitekeyPlaceholder/g, sitekey))
                });
            });
        } else {
            const request = net.request(req)
            request.on('response', res => {
                const chunks = []

                res.on('data', chunk => {
                    chunks.push(Buffer.from(chunk))
                })

                res.on('end', async () => {
                    const file = Buffer.concat(chunks)
                    callback(file)
                })
            })

            if (req.uploadData) {
                req.uploadData.forEach(part => {
                    if (part.bytes) {
                        request.write(part.bytes)
                    } else if (part.file) {
                        request.write(readFileSync(part.file))
                    }
                })
            }

            request.end()
        }
    })
};