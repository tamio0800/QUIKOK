(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-3064fe14"],{"2eab":function(t,e){t.exports="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAF8AAABfCAYAAACOTBv1AAAACXBIWXMAABcRAAAXEQHKJvM/AAAE70lEQVR42u2d7XGbQBCGX2vy36SCkApMKjDugA5COnAqCOlAJZAKgjsgHeAKgjpAFVx+aHEYLKS7Y5cv7TvDZBzjE3pub2+X24M7YwxWpgBA1Pu/mo5V6cNCryvqHQGAB8u/PQKoOh1S0s/N0r7k3UIsPwIQA0gAPAp9xit1RAmguHX4IYCUjk8Tf/aROiCnzrgZ+AmAZ0ELd9UBwJ46otkq/BRANoOVu4yGPR3NVuAn9IWWCn22TpCEH9JQfsQ6dSD3KDY574TazQD8XTF40Ej9TRNyuAbLD8lSHrAtHWnOKpZq+QklM1sDDwD3NAr2S7T8DMAP3IZeKSFslmD5+Q2BB43sEu/vL01q+QH5wEfcpo40Aqqp4QfU+w+4bY3qAF+3Uyj4t4nY2wX5wF9z4iTZAYE0/AzAV+XN0wEuPj+hWFc1rF+UjLHCD2lSuVe+V/XdNhmzhb/VzFVKX2wiIBufnyl4r6BktOWHON2dVLnrJxmuN/xSw8pRCViECyUtuyvRjYIfF356W36N9Sz9LVlPGKiQGLL8VMGzKXO1fLX6CULP3YCvV/C8era1fI1wZPQRvdWv3Zm4XsHLKL3mdlJlNJ3r6bsdnWgnnHi7lh8peHElQ24nVjbzwU+Ujbge0Fnt6sLXKGcaxX34kTKZTJHCV8tXy1f40+qtCKHdhxsIfMhLJ6Fot3reM7ZdUvsxHRwBwwGnary2Dj+krJ87GIkBlDDGwPCqMsaE1G73CIwxOUPb0Zm2YYyJjTHNiLZzukaJtvuKjTHghl8OXHz38O2A5gKc9og8IRUW1x0xckqNMdgxupyjZaKW0vD2uTF1bUNChSvrpgPXnVqcV+FUkcahsJ1wuSbbAva7NTIPX5xbnrsXvG7WbUGce7JcNouVjm3Xjuf/EWq7Wir8RhBmjQ2KE76L+4oF237zqQLnRtzwuawqEToXON0NDB069pPjtQRC1z0Z/EdLiw7ht1wpNeHeW/5NBO5dl8xxfnMhCWoTrWpkInSp7Vyo7UgyyWqYs9ysl+UGlFhwfE5NbbXth/RzzdT2M8GJjTEJQ1Y+CL9dQC8ht5hyhO5o6esjgGY3QSin4AfC8ingqwYSwJ1nxqny17u6nUqZzAe/welRJip5leduL6jrkdehO78q/Jmsvg+/oJhcJadiCP67X6rYk82L8HNlNI3VA+e3BdXQUnEJvdsUd24xZa+c2PUKy92IuU687Dpr0OfgN2r97LF9bgu/7Sm1fh5lQ78Ygq/WL2z1Q9FOq4AmCY18/PV06c7BpdKRBgPb1lVWesGVWzY2z1grofu1fLLZEFcKyWyKphKdfJ1lU9RrBb+BPhbA1d3kNifalgsW4CuP3noma22oLrWatbK96udTOBQM75QZm1I4roUrfB59g8daiMLnAZ/7/KHCnwm8wp8RPLDclxGvIaoZvd6tlu8ex8dgKjRwgX/rJYUvGPlqpr5cX9VU4/ZuMR9xuleTczfs6nYSuO1x3YK1hxAqqXGF3z7l487y+Ix13hM64LQQkkDwhcTSE25NkcHTSkbMgULIEBPUrk79AvqI/OfS3rX1iv8voZ9MU8NvFdCIeJ5xAm9rJ/dzRXJzwe+PhoQO6bcSHcidFFhAUfAS4PdHRIz/jwWLMG434x+y6oqg10v6skuDP6SY/g1x+RkMZScqa5b+pdYCf5P6B+LezEMhy6CEAAAAAElFTkSuQmCC"},"427d":function(t,e,o){"use strict";o.r(e);var n=function(){var t=this,e=t.$createElement,o=t._self._c||e;return o("v-app",{attrs:{id:"main-view"}},[o("core-toolbar"),o("v-content",{style:"padding-left: 0px;"},[o("v-fade-transition",{attrs:{mode:"out-in"}},[o("router-view")],1)],1),t._e(),o("Chatroom",{directives:[{name:"show",rawName:"v-show",value:t.chatView,expression:"chatView"}],on:{snackbar:t.doSnackbar}}),o("div",{attrs:{id:"chat-icon"},on:{click:function(e){return t.doOpenChat()}}},[t.chatView?t._e():o("div",{staticClass:"cursor",class:{active:t.doReadStatus}},[o("img",{attrs:{src:t.ChatIcon}})]),t.chatView?o("div",{staticClass:"cursor text-white close"},[o("v-icon",[t._v("mdi-close")])],1):t._e()]),t.isTeacherCB||t.isStudentCB?o("div",{attrs:{id:"chatLog"}},t._l(t.chatLog,(function(e,n){return o("p",{key:"l"+n,style:"color:"+e.value},[t._v(" "+t._s(e.text)+" ")])})),0):t._e(),o("core-footer")],1)},r=[],a=(o("8e6e"),o("ac6a"),o("456d"),o("bd86")),i=o("2f62"),s=o("4360"),c=o("2f77"),u=o("2eab"),h=o.n(u);function d(t,e){var o=Object.keys(t);if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(t);e&&(n=n.filter((function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable}))),o.push.apply(o,n)}return o}function f(t){for(var e=1;e<arguments.length;e++){var o=null!=arguments[e]?arguments[e]:{};e%2?d(Object(o),!0).forEach((function(e){Object(a["a"])(t,e,o[e])})):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(o)):d(Object(o)).forEach((function(e){Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(o,e))}))}return t}var l={name:"MainView",components:{Chatroom:c["default"]},metaInfo:function(){return{title:this.appName}},beforeRouteEnter:function(t,e,o){s["a"].state.fromPath=e.fullPath,s["a"].state.toPath=t.fullPath,o()},data:function(){return{ChatIcon:h.a,chatView:!1,chatLog:[]}},computed:f({},Object(i["c"])(["root","appName","fromPath","toPath","isProduction","dologinView","doChatView","doReadStatus"]),{userInfo:function(){return JSON.parse(localStorage.getItem("user"))},isTeacherCB:function(){return!!this.userInfo&&this.userInfo.group.indexOf("test_teacher")>-1},isStudentCB:function(){return!!this.userInfo&&this.userInfo.group.indexOf("test_student")>-1}}),watch:{"$route.fullPath":function(t){this.doGtagsPageview()},doChatView:function(t){this.chatView=t},chatView:function(t){this.$store.state.doChatView=t}},mounted:function(){this.doGtagsPageview()},methods:{doOpenMessage:function(){window.open("https://reurl.cc/XeDE93","_blank")},doGtagsPageview:function(){this.$store.state.root=this.$http.defaults.baseURL,this.$store.state.isProduction="https://www.quikok.com"===this.root,this.isProduction&&this.$gtag.pageview({from_path:this.fromPath,page_path:this.toPath,hostname:this.root,user_id:this.userInfo?this.userInfo.user_id:-1})},doOpenChat:function(){localStorage.getItem("token")?this.chatView=!this.chatView:this.$store.state.dologinView=!0},doSnackbar:function(t){this.chatLog.push({value:t[0],text:t[1]})}}},w=l,p=(o("b32a"),o("2877")),A=Object(p["a"])(w,n,r,!1,null,null,null);e["default"]=A.exports},b32a:function(t,e,o){"use strict";var n=o("c6b8"),r=o.n(n);r.a},c6b8:function(t,e,o){}}]);
//# sourceMappingURL=chunk-3064fe14.fc7407f7.js.map