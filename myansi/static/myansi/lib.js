import API from "./api.js";
import { CookieContext } from "./context.js";
import { SETTINGS } from "./settings.js";


class Notify {
    constructor(position){
        this.position = position;
    }
    getNofity(){
        switch (this.position.getValue()) {
            case 'top-left':
                return VuetifyMessageSnackbar.Notify.topLeft();
            case 'top':
                return VuetifyMessageSnackbar.Notify.top();
            case 'top-right':
                return VuetifyMessageSnackbar.Notify.topRight();
            case 'bottom-left':
                return VuetifyMessageSnackbar.Notify.bottomLeft();
            case 'bottom':
                return VuetifyMessageSnackbar.Notify.bottom();
            case 'bottom-right':
                return VuetifyMessageSnackbar.Notify.bottomRight();
            default:
                return VuetifyMessageSnackbar.Notify.topRight();
        }
    }
    warn(msg, timeout=3) {
        this.getNofity().timeout(timeout * 1000).warning(msg);
    };
    info(msg, timeout = 3) {
        this.getNofity().timeout(timeout * 1000).info(msg);
    };
    success(msg, timeout = 2) {
        this.getNofity().timeout(timeout * 1000).success(msg);
    };
    error(msg, timeout = 5) {
        this.getNofity().timeout(timeout * 1000).error(msg)
    };
}

export class Message extends Notify {

    constructor(){
        super(SETTINGS.getItem('messagePosition'));
    }
}

export class Alert extends Notify {
    constructor(){
        super(SETTINGS.getItem('alertPosition'));
    }
}

const KB = 1024;
const MB = KB * 1024;
const GB = MB * 1024;

export class Utils {

    static nowFormat(dateObject=null) {
        let date = dateObject ? dateObject : new Date();
        let month = date.getMonth() + 1;
        let day = date.getDate()
        let hours = date.getHours();
        let minutes = date.getMinutes();
        let seconds = date.getSeconds();
        return `${date.getFullYear()}-${month >= 10 ? month : '0' + month}-${day >= 10 ? day : '0' + day} ` +
            `${hours >= 10 ? hours : '0' + hours}:${minutes >= 10 ? minutes : '0' + minutes}:${seconds >= 10 ? seconds : '0' + seconds}`;
    }
    static parseUTCToLocal(utcString){
        if (! utcString) {
            return '';
        }
        if (! utcString.endsWith('Z')){
            utcString += 'Z'
        }
        return Utils.nowFormat(new Date(`${utcString}`))
    }
    static getRandomName(prefix = null) {
        let date = this.nowFormat()
        return prefix ? `${prefix}-${date}` : date;
    }
    static checkVolumeStatus(volume_id) {
        API.volume.show(volume_id).then(resp => {
            let status = resp.data.volume.status;
            if (status == 'available') {
                MESSAGE.success(`卷 ${volume_id} 创建成功`);
                volumeTable.refresh()
                return;
            } else if (status == 'error') {
                MESSAGE.error(`卷 ${volume_id} 创建失败`);
                volumeTable.refresh();
                return;
            };
            setTimeout(function () {
                Utils.checkVolumeStatus(volume_id)
            }, 5 * 1000)
        });
    }
    static checkVolumeAttached(volume_id) {
        API.volume.show(volume_id).then(resp => {
            let status = resp.data.volume.status;
            if (status == 'in-use') {
                MESSAGE.success(`卷 ${volume_id} 挂载成功`);
                return;
            } else if (status == 'error') {
                MESSAGE.error(`卷 ${volume_id} 挂载失败`);
                return;
            };
            setTimeout(function () {
                Utils.checkVolumeAttached(volume_id)
            }, 3 * 1000)
        });
    }
    static checkVolumeDetached(volume_id) {
        API.volume.show(volume_id).then(resp => {
            let status = resp.data.volume.status;
            if (status == 'available') {
                MESSAGE.success(`卷 ${volume_id} 卸载成功`);
                return;
            } else if (status == 'error') {
                MESSAGE.error(`卷 ${volume_id} 卸载失败`);
                return;
            };
            setTimeout(function () {
                Utils.checkVolumeDetached(volume_id)
            }, 5 * 1000)
        });
    }
    static humanRam(size) {
        if (size < 1024) {
            return `${size} MB`
        }
        return `${(size / 1024).toFixed(0)} GB`
    }
    static humanSize(size) {
        if (size == null){
            return ''
        } else if (size <= KB) {
            return `${size} B`
        } else if (size <= MB) {
            return `${(size / KB).toFixed(2)} KB`
        } else if (size <= GB) {
            return `${(size / MB).toFixed(2)} MB`
        } else {
            return `${(size / GB).toFixed(2)} GB`
        }
    }
    static sleep(seconds) {
        seconds = (seconds || 0);
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                resolve(true);
            }, seconds * 1000)
        })
    }
    static copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text);
        } else {
            let element = document.createElement('input', text)
            element.setAttribute('value', text);
            document.body.appendChild(element)
            element.select();
            document.execCommand('copy');
            document.body.removeAttribute(element);
        }
    }
    static lastDateList(steps, nums){
        // Get last n list of date
        // e.g. [timestamp1, timestamp2, ...]
        let endDate = new Date();
        let dateList = [];
        for (let i = 0; i < nums; i++){
            for (let unit in steps) {
                switch (unit) {
                    case 'hour':
                        endDate.setHours(endDate.getHours() - steps.hour);
                        break;
                    case 'month':
                        endDate.setMonth(endDate.getMonth() - steps.month)
                        break;
                    case 'day':
                        endDate.setDate(endDate.getDate() - steps.day);
                        break;
                    case 'year':
                        endDate.setFullYear(endDate.getFullYear() - steps.year);
                        break;
                    default:
                        throw Error(`Invalid step unit ${unit}`);
                }
            }
            dateList.push(endDate.getTime());
        }
        return dateList.reverse();
    }
}

//             error  warning info debug
// logLevels = [0,    1,      2,   3]
export var Level = {
    ERROR: 0,
    WARNING: 1,
    INFO: 2,
    DEBUG: 3,
}

export class Logger {
    constructor(kwargs = {}) {
        this.level = kwargs['level'] || Level.INFO;
    }
    debug(msg) {
        if (this.level < Level.DEBUG){
            return
        }
        console.debug(new Date().toLocaleString(), 'DEBUG', msg)
    };
    info(msg) {
        if (this.level < Level.INFO){
            return
        }
        console.info(`${new Date().toLocaleString()} INFO ${msg}`)
    };
    warn(msg) {
        if (this.level < Level.WARNING){
            return
        }
        console.warn(`${new Date().toLocaleString()} WARN ${msg}`)
    };
    error(msg) {
        console.error(`${new Date().toLocaleString()} ERROR ${msg}`)
        VuetifyMessageSnackbar.Notify.top().timeout(timeout * 1000).error(msg)
    };
}

export class ContextLocalStorage {
    constructor(){
        this.context = new CookieContext();
    }
    domain(){
        return `${this.context.getClusterId()}_${this.context.getRegion() || ''}`;
    }
    getAll(name){
        let itemName = `${this.domain()}_${name}`
        LOG.debug(`localStorage get Item ${itemName}`)
        let data = localStorage.getItem(itemName)
        return data ? JSON.parse(data): {};
    }
    get(name, key){
        let itemName = `${this.domain()}_${name}`
        return this.getAll(itemName)[key]
    }
    set(name, key, value) {
        let data = this.getAll(name)
        data[key] = value;
        let itemName = `${this.domain()}_${name}`
        LOG.debug(`localStorage save item: ${itemName} -> ${key} (${JSON.stringify(data)})`)
        localStorage.setItem(itemName, JSON.stringify(data));
    }
    delete(name, key) {
        let itemName = `${this.domain()}_${name}`
        let data = this.getAll(name)
        LOG.debug(`localStorage delete Item: ${itemName} -> ${key}`)
        delete data[key];
        localStorage.setItem(itemName, JSON.stringify(data));
    }
}

export class ServerTasks extends ContextLocalStorage {

    getAll(){
        return super.getAll('tasks');
    }
    add(serverId, task) {
        LOG.debug(`save task ${serverId} ${task}`);
        super.set('tasks', serverId, 'building');
    }
    delete(serverId) {
        super.delete('tasks', serverId);
        LOG.debug(`delete task ${serverId}`);
        localStorage.removeItem(serverId);
    }
}

export var CONST = {
    // service name
    NOVA_COMPUTE: 'nova-compute',
    // unit
    UNIT_KB: 1024,
    UNIT_MB: 1024 * 1024,
    UNIT_GB: 1024 * 1024 * 1024,

    UNIT_1000: 1000,
    UNIT_1000_000: 1000000,
    // usage range of time
    USAGE_LAST_1_DAY: 'last1Day',
    USAGE_LAST_7_DAY: 'last7Days',
    USAGE_LAST_6_MONTHES: 'last6Monthes',
    USAGE_LAST_1_YEAR: 'last1Year',
}

export class DataTable {
    constructor(headers, api, bodyKey = null, name = '') {
        this.headers = headers;
        this.api = api;
        this.bodyKey = bodyKey;
        this.name = name;
        this.itemsPerPage = 10;
        this.search = '';
        this.items = [];
        this.statistics = {};
        this.selected = []
        this.extendItems = []
        this.newItemDialog = null;
    }
    async openNewItemDialog(){
        if (this.newItemDialog){
            this.newItemDialog.open();
        }
    }
    async createNewItem(){
        if (this.newItemDialog) {
            await this.newItemDialog.commit();
            this.refresh();
        }
    }
    async deleteSelected() {
        if (this.selected.length == 0) {
            return;
        }
        MESSAGE.info(`${this.name} 删除中`)
        for (let i in this.selected) {
            let item = this.selected[i];
            try {
                await this.api.delete(item.id || item.name);
                this.waitDeleted(item.id || item.name);
            } catch {
                MESSAGE.error(`删除 ${this.name} ${item.id} 失败`)
            }
        }
        MESSAGE.success('删除完成');
        this.refresh();
        this.resetSelected();
    }
    async waitDeleted(id) {
        while (true) {
            let body = await this.api.list({ id: id })
            if (body[this.bodyKey].length == 0) {
                MESSAGE.success(`${this.name} ${id} 删除成功`, 2);
                this.refresh();
                break;
            }
            await Utils.sleep(5);
        }
    }
    resetSelected() {
        this.selected = [];
    }
    updateItem(newItem) {
        for (var i = 0; i < this.items.length; i++) {
            if (this.items[i].id != newItem.id) {
                continue;
            }
            for (var key in newItem) {
                this.items[i][key] = newItem[key];
            }
            break
        }
    }
    async refresh(filters = {}) {
        let result = null
        if (this.api.detail) {
            result = await this.api.detail(filters);
        } else {
            result = await this.api.list(filters)
        }
        this.items = this.bodyKey ? result[this.bodyKey] : resp;
        return result;
    };
}
export class CommandTable extends DataTable {
    constructor() {
        super([{ text: '主机', value: 'hostname' },
                { text: '状态', value: 'status' },
                { text: '返回码', value: 'rc' },
                { text: '说明', value: 'msg' },
                { text: '开始时间', value: 'start' },
                { text: '结束时间', value: 'end' },
              ], API.command, 'command', '实例');
    }
    add(host, status, result){
        this.items.push({
            'hostname': host,
            'status': status,
            'start': result.start,
            'end': result.end,
            'delta': result.delta,
            'msg': result.msg,
            'stdout_lines': result.stdout_lines,
            'stderr_lines': result.stderr_lines,
            'rc': result.rc
        });
    }
    clear(){
        this.items = [];
    }
    getOutput(result){
        if (result.stderr_lines && result.stderr_lines.length > 0){
            return result.stderr_lines.join('\n')
        } else if (result.stdout_lines && result.stdout_lines.length > 0 ){
            return result.stdout_lines.join('\n')
        }
        return ''
    }
}

export class CommandView {
    constructor(){
        this.group = 'all';
        this.host = null;

        this.cmd = 'hostname'
        this.running = false;
        this.table = new CommandTable();
        this.hosts = {'all': []};
    }
    async listHosts(){
        let hosts = (await API.host.list()).hosts;
        for (let group in hosts){
            this.hosts[group] = hosts[group];
        }
    }
    async run() {
        if (! this.cmd){
            return;
        }
        let data = {
            host: this.host ? this.host : this.group,
            cmd: this.cmd
        }
        this.running = true;
        this.table.clear();
        let result = {};
        try {
            result = (await API.command.post(data)).result
        } catch (e) {
            throw e
        } finally {
            this.running = false;
        }
        for (let host in result.ok){
            this.table.add(host, 'ok', result.ok[host]);
        };
        for (let host in result.failed){
            this.table.add(host, 'failed', result.failed[host]);
        };
        for (let host in result.unreachable){
            this.table.add(host, 'unreachable', result.unreachable[host]);
        };
    }

}

export const MESSAGE = new Message();
export const ALERT = new Alert();
export const LOG = new Logger({level: Level.DEBUG});
