var COOKIE_DRIVER = null;

export class CookieContext{
    constructor() {
        if (! COOKIE_DRIVER){
            console.error(`COOKIE_DRIVER is null`);
        }
        this.cookies = COOKIE_DRIVER;
    }
    setClusterId(clusterId){
        return this.cookies.set('clusterId', clusterId)
    }
    setRegion(region){
        return this.cookies.set('region', region)
    }
    getClusterId(){
        return this.cookies.get('clusterId')
    }
    getClusterName(){
        return this.cookies.get('clusterName')
    }
    getRegion(){
        return this.cookies.get('region')
    }
}

export function init(cookieDriver){
    COOKIE_DRIVER = cookieDriver;
}
