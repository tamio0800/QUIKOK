(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-3064fe14"],{"2eab":function(t,e){t.exports="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAF8AAABfCAYAAACOTBv1AAAACXBIWXMAABcRAAAXEQHKJvM/AAAE70lEQVR42u2d7XGbQBCGX2vy36SCkApMKjDugA5COnAqCOlAJZAKgjsgHeAKgjpAFVx+aHEYLKS7Y5cv7TvDZBzjE3pub2+X24M7YwxWpgBA1Pu/mo5V6cNCryvqHQGAB8u/PQKoOh1S0s/N0r7k3UIsPwIQA0gAPAp9xit1RAmguHX4IYCUjk8Tf/aROiCnzrgZ+AmAZ0ELd9UBwJ46otkq/BRANoOVu4yGPR3NVuAn9IWWCn22TpCEH9JQfsQ6dSD3KDY574TazQD8XTF40Ej9TRNyuAbLD8lSHrAtHWnOKpZq+QklM1sDDwD3NAr2S7T8DMAP3IZeKSFslmD5+Q2BB43sEu/vL01q+QH5wEfcpo40Aqqp4QfU+w+4bY3qAF+3Uyj4t4nY2wX5wF9z4iTZAYE0/AzAV+XN0wEuPj+hWFc1rF+UjLHCD2lSuVe+V/XdNhmzhb/VzFVKX2wiIBufnyl4r6BktOWHON2dVLnrJxmuN/xSw8pRCViECyUtuyvRjYIfF356W36N9Sz9LVlPGKiQGLL8VMGzKXO1fLX6CULP3YCvV/C8era1fI1wZPQRvdWv3Zm4XsHLKL3mdlJlNJ3r6bsdnWgnnHi7lh8peHElQ24nVjbzwU+Ujbge0Fnt6sLXKGcaxX34kTKZTJHCV8tXy1f40+qtCKHdhxsIfMhLJ6Fot3reM7ZdUvsxHRwBwwGnary2Dj+krJ87GIkBlDDGwPCqMsaE1G73CIwxOUPb0Zm2YYyJjTHNiLZzukaJtvuKjTHghl8OXHz38O2A5gKc9og8IRUW1x0xckqNMdgxupyjZaKW0vD2uTF1bUNChSvrpgPXnVqcV+FUkcahsJ1wuSbbAva7NTIPX5xbnrsXvG7WbUGce7JcNouVjm3Xjuf/EWq7Wir8RhBmjQ2KE76L+4oF237zqQLnRtzwuawqEToXON0NDB069pPjtQRC1z0Z/EdLiw7ht1wpNeHeW/5NBO5dl8xxfnMhCWoTrWpkInSp7Vyo7UgyyWqYs9ysl+UGlFhwfE5NbbXth/RzzdT2M8GJjTEJQ1Y+CL9dQC8ht5hyhO5o6esjgGY3QSin4AfC8ingqwYSwJ1nxqny17u6nUqZzAe/welRJip5leduL6jrkdehO78q/Jmsvg+/oJhcJadiCP67X6rYk82L8HNlNI3VA+e3BdXQUnEJvdsUd24xZa+c2PUKy92IuU687Dpr0OfgN2r97LF9bgu/7Sm1fh5lQ78Ygq/WL2z1Q9FOq4AmCY18/PV06c7BpdKRBgPb1lVWesGVWzY2z1grofu1fLLZEFcKyWyKphKdfJ1lU9RrBb+BPhbA1d3kNifalgsW4CuP3noma22oLrWatbK96udTOBQM75QZm1I4roUrfB59g8daiMLnAZ/7/KHCnwm8wp8RPLDclxGvIaoZvd6tlu8ex8dgKjRwgX/rJYUvGPlqpr5cX9VU4/ZuMR9xuleTczfs6nYSuO1x3YK1hxAqqXGF3z7l487y+Ix13hM64LQQkkDwhcTSE25NkcHTSkbMgULIEBPUrk79AvqI/OfS3rX1iv8voZ9MU8NvFdCIeJ5xAm9rJ/dzRXJzwe+PhoQO6bcSHcidFFhAUfAS4PdHRIz/jwWLMG434x+y6oqg10v6skuDP6SY/g1x+RkMZScqa5b+pdYCf5P6B+LezEMhy6CEAAAAAElFTkSuQmCC"},"427d":function(t,e,n){"use strict";n.r(e);var r=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("v-app",{attrs:{id:"main-view"}},[n("core-toolbar"),n("v-content",{style:"padding-left: 0px;"},[n("v-fade-transition",{attrs:{mode:"out-in"}},[n("router-view")],1)],1),t.isTeacherCB||t.isStudentCB?n("Chatroom",{directives:[{name:"show",rawName:"v-show",value:t.chatView,expression:"chatView"}],on:{snackbar:t.doSnackbar}}):t._e(),t.isTeacherCB||t.isStudentCB?n("div",{attrs:{id:"chat-icon"},on:{click:function(e){return t.doOpenChat()}}},[t.chatView?t._e():n("div",{staticClass:"cursor-no-hover",class:{active:t.doReadStatus}},[n("img",{attrs:{src:t.ChatIcon}})]),t.chatView?n("div",{staticClass:"cursor-no-hover text-white close"},[n("v-icon",[t._v("mdi-close")])],1):t._e()]):t._e(),t.isTeacherCB||t.isStudentCB?n("div",{staticClass:"chatLog"},t._l(t.chatLog,(function(e,r){return n("p",{key:"l"+r,style:"color:"+e.value},[t._v(" "+t._s(e.text)+" ")])})),0):t._e(),n("core-footer")],1)},o=[],a=(n("8e6e"),n("ac6a"),n("456d"),n("bd86")),c=n("2f62"),i=n("2f77"),s=n("2eab"),u=n.n(s);function h(t,e){var n=Object.keys(t);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(t);e&&(r=r.filter((function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable}))),n.push.apply(n,r)}return n}function d(t){for(var e=1;e<arguments.length;e++){var n=null!=arguments[e]?arguments[e]:{};e%2?h(Object(n),!0).forEach((function(e){Object(a["a"])(t,e,n[e])})):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(n)):h(Object(n)).forEach((function(e){Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(n,e))}))}return t}var l={name:"MainView",components:{Chatroom:i["default"]},metaInfo:function(){return{title:this.appName}},data:function(){return{ChatIcon:u.a,chatView:!1,chatLog:[]}},computed:d({},Object(c["c"])(["appName","dologinView","doChatView","doReadStatus"]),{userInfo:function(){return JSON.parse(localStorage.getItem("user"))},isTeacherCB:function(){return!!this.userInfo&&this.userInfo.group.indexOf("test_teacher")>-1},isStudentCB:function(){return!!this.userInfo&&this.userInfo.group.indexOf("test_student")>-1}}),watch:{doChatView:function(t){this.chatView=t},chatView:function(t){this.$store.state.doChatView=t}},methods:{doOpenChat:function(){localStorage.getItem("token")?this.chatView=!this.chatView:this.$store.state.dologinView=!0},doSnackbar:function(t){this.chatLog.push({value:t[0],text:t[1]})}}},f=l,A=(n("b32a"),n("2877")),w=Object(A["a"])(f,r,o,!1,null,null,null);e["default"]=w.exports},b32a:function(t,e,n){"use strict";var r=n("c6b8"),o=n.n(r);o.a},c6b8:function(t,e,n){}}]);
//# sourceMappingURL=chunk-3064fe14.0ae0f5cc.js.map