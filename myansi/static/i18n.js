const MESSAGES = {
    'en': {
        language: 'language',
        enUS: 'en_US',
        zhCN: 'zh_CN',
        setting: 'setting',
        reset: 'reset',
        save: 'save',
        name: 'name',
        messagePosition: 'message position',
        alertPosition: 'alert position',
        security: 'security',
        region: 'Region',
        theme: "theme",
        navigatorWidth: 'navigator width',
        refresh: 'refresh',
        cluster: 'cluster',

        status: 'status',
        hostName: 'hostname',
        usedAndTotalMemory: 'used/total Memory',
        usedAndTotalCPU: 'used/total CPU',
        ipAddress: 'IP address',
        hypervisorVersion: 'hypervisor version',

        tenantUsage: 'tenant usage',
        last1Day: 'last 1 day',
        last7Days: 'last 7 days',
        last6Monthes: 'last 6 monthes',
        last1Year: 'last 1 year',
        newService: 'new service',
        service: 'service',
        new: 'new',
    },
    'zh-CN': {
        language: '语言',
        enUS: '英文',
        zhCN: '简体中文',
        setting: '设置',
        reset: '重置',
        save: '保存',
        name: '名字',
        messagePosition: '消息框显示位置',
        alertPosition: '警告框显示位置',
        security: '安全',
        region: '地区',
        theme: "主题",
        navigatorWidth: '侧边栏宽度',
        refresh: '刷新',
        cluster: '集群',

        status: '状态',
        hostName: '主机名',
        usedAndTotalMemory: '已用内存/总内存',
        usedAndTotalCPU: '已用CPU/总CPU',
        ipAddress: 'IP地址',
        hypervisorVersion: '虚拟机版本',

        cpu: 'CPU',
        memory: '内存',
        localDisk: '本地磁盘',
        disk: '磁盘',
        vm: '虚拟机',
        instance: '实例',
        instanceNum: '虚拟机数量',
        node: '节点',

        tenantUsage: '资源使用情况',
        last1Day: '最近1天',
        last7Days: '最近7天',
        last6Monthes: '最近6个月',
        last1Year: '最近1年',
        newService: '新建服务',
        service: '服务',
        new: '新建',
    },
};

function getUserSettedLang() {
    return localStorage.getItem('language');
}

class I18n extends VueI18n {
    constructor(){
        super({locale: localStorage.getItem('language') || navigator.language || 'zh-CN', messages: MESSAGES});
    }

    setDisplayLang(language) {
        if(language){
            this.locale = language;
            localStorage.setItem('language', this.locale)
        };
    }
}

export const I18N = new I18n();


