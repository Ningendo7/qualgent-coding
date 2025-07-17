// tests/onboarding.spec.js
import { remote } from 'webdriverio';

async function runTest(platform, searchText) {
    const capabilities = {
        browserName: 'Chrome',
        'bstack:options': {
            os: platform === 'android' ? 'Android' : 'iOS',
            osVersion: platform === 'android' ? '13' : '16',
            deviceName: platform === 'android' ? 'Samsung Galaxy S22' : 'iPhone 14',
            buildName: 'Qualgent Build',
            sessionName: `Onboarding Test - ${platform}`,
            debug: true,
        }
    };

    const browser = await remote({
        protocol: 'https',
        hostname: 'hub.browserstack.com',
        port: 443,
        path: '/wd/hub',
        user: process.env.BS_USERNAME,
        key: process.env.BS_ACCESS_KEY,
        capabilities
    });

    try {
        await browser.url('https://en.wikipedia.org/wiki/Cristiano_Ronaldo');
        const bodyText = await browser.$('body').getText();

        if (bodyText.includes(searchText)) {
            console.log(`✅ '${searchText}' found on ${platform}!`);
        } else {
            console.log(`❌ '${searchText}' NOT found on ${platform}!`);
        }
    } finally {
        await browser.deleteSession();
    }
}

if (process.argv.length < 4) {
    console.error('Usage: node onboarding.spec.js <platform> <searchText>');
    process.exit(1);
}

const platform = process.argv[2];
const searchText = process.argv[3];

runTest(platform, searchText).catch(console.error);
