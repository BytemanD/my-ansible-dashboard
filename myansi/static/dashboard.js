import { ALERT, CommandView, MESSAGE, Utils } from "./myansi/lib.js";
import API from "./myansi/api.js";
// import * as echarts from 'echarts';
// import { TreeChart } from 'echarts/charts';
// echarts.use([TreeChart]);
import { SETTINGS } from "./myansi/settings.js";
import { I18N } from "./i18n.js";


const navigationItems = [
    { title: '概览', icon: 'mdi-view-dashboard' },
    { title: '命令', icon: 'mdi-console-line', group: '作业' },
    { title: '任务', icon: 'mdi-play', },
]
// init cookies
if (!$cookies.get('navigationItem') || !navigationItems[$cookies.get('navigationItem')]){
    $cookies.set('navigationItem', 0);
}

new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    vuetify: new Vuetify(),
    data: {
        ui: {
            theme: SETTINGS.getItem('theme'),
            navigatorWidth: SETTINGS.getItem('navigatorWidth'),
        },
        UTILS: Utils,
        clusterTable: [],
        settings: SETTINGS,
        I18N: I18N,
        navigation: {
            item: $cookies.get('navigationItem'),
            items: navigationItems,
        },
        drawer: true,
        miniVariant: false,
        commandView: new CommandView(),
    },
    methods: {
        getServices: async function () {
            let body = await API.service.list()
            body.services.forEach(item => {
                this.identity.serviceMap[item.id] = item
            });
        },
        loginVnc: async function (server) {
            let body = await API.server.getVncConsole(server.id);
            window.open(body.remote_console.url, '_blank');
        },
        refreshContainer: function () {
            if (this.navigation.item >= this.navigation.items.length) {
                this.navigation.item = 0;
            }
            switch (this.navigation.items[this.navigation.item].title) {
                case '概览':
                    break;
                case '命令':
                    break;
                case '任务':
                    break;
            }
        },
        useCluster: function () {
            let cluster = this.clusterTable.getSelectedCluster()
            if (cluster){
                $cookies.set('clusterId', cluster.id);
                $cookies.set('clusterName', cluster.name);
                window.open('/dashboard', '_self');
            }
        },
        useRegion: function(){
            if (! this.regionTable.selected){
                $cookies.remove('region');
            } else {
                $cookies.set('region', this.regionTable.selected);
            }
            window.open('/dashboard', '_self');
        },
        drawAz() {
            this.computing.azTable.drawTopoloy('az');
        },
        saveSettings(){
            this.settings.save();
            MESSAGE.success('配置已保存');
        },
        resetSettings(){
            this.settings.reset();
            MESSAGE.success('配置已重置');
        },
    },
    mounted: function () {
        // this.drawAz();
    },
    created: async function () {
        let loader = document.getElementById('loader');
        if (loader){
            loader.remove()
        }
    },
    watch: {
        'navigation.item': {
            handler(newValue, oldValue) {
                if (newValue != undefined) {
                    this.$cookies.set('navigationItem', newValue);
                }
                this.refreshContainer();
            },
        },
    }
});
