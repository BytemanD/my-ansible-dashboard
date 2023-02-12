import { Utils, MESSAGE, ALERT, LOG, ServerTasks, Alert, CONST } from './lib.js';
import API from './api.js';
import { I18N } from '../i18n.js';


class Dialog {
    constructor(params) {
        this.name = null;
        this.resource = 'resource';
        this.show = false;
        this.params = params || {};
        this.errorMessage = null;
    }
    refreshName() {
        this.name = this.randomName();
    }
    randomName() {
        return Utils.getRandomName(this.resource);
    }
    open() {
        this.errorMessage = null;
        this.display()
    }
    display() {
        this.show = true;
    }
    hide() {
        this.show = false;
    }
    checkNotNull(value) {
        if (! value) {
            return '该选项不能为空';
        }
        return true;
    }
    checkNameNotNull(value) {
        if (! value) {
            return '名字不能为空';
        }
        return true;
    }
    checkNotEmpty(value, message){
        if (value == null || (value instanceof Array && value.length == 0) || Object.keys(value).length == 0){
            throw Error(message)
        }
    }
    formatTime(dateTime){
        return dateTime ? Utils.parseUTCToLocal(dateTime) : '';
    }
}

export default Dialog;
