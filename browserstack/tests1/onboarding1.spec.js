const { remote } = require("webdriverio");

(async () => {
  const browser = await remote({
    protocol: 'https',
    hostname: 'hub.browserstack.com',
    port: 443,
    path: '/wd/hub',
    logLevel: 'info',
    capabilities: {
      'bstack:options': {
        os: "Windows",
        osVersion: "11",
        buildName: "Qualgent Build",
        sessionName: "Onboarding Test",
        userName: process.env.BROWSERSTACK_USERNAME,
        accessKey: process.env.BROWSERSTACK_ACCESS_KEY,
      },
      browserName: "Chrome",
    },
  });

  try {
    await browser.url("https://example.com");
    await browser.pause(5000); // wait 5 seconds so you can see the page loaded
  } finally {
    await browser.deleteSession();
  }
})();
