(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-7abbd76e"],{"2eab":function(t,e){t.exports="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAF8AAABfCAYAAACOTBv1AAAACXBIWXMAABcRAAAXEQHKJvM/AAAE70lEQVR42u2d7XGbQBCGX2vy36SCkApMKjDugA5COnAqCOlAJZAKgjsgHeAKgjpAFVx+aHEYLKS7Y5cv7TvDZBzjE3pub2+X24M7YwxWpgBA1Pu/mo5V6cNCryvqHQGAB8u/PQKoOh1S0s/N0r7k3UIsPwIQA0gAPAp9xit1RAmguHX4IYCUjk8Tf/aROiCnzrgZ+AmAZ0ELd9UBwJ46otkq/BRANoOVu4yGPR3NVuAn9IWWCn22TpCEH9JQfsQ6dSD3KDY574TazQD8XTF40Ej9TRNyuAbLD8lSHrAtHWnOKpZq+QklM1sDDwD3NAr2S7T8DMAP3IZeKSFslmD5+Q2BB43sEu/vL01q+QH5wEfcpo40Aqqp4QfU+w+4bY3qAF+3Uyj4t4nY2wX5wF9z4iTZAYE0/AzAV+XN0wEuPj+hWFc1rF+UjLHCD2lSuVe+V/XdNhmzhb/VzFVKX2wiIBufnyl4r6BktOWHON2dVLnrJxmuN/xSw8pRCViECyUtuyvRjYIfF356W36N9Sz9LVlPGKiQGLL8VMGzKXO1fLX6CULP3YCvV/C8era1fI1wZPQRvdWv3Zm4XsHLKL3mdlJlNJ3r6bsdnWgnnHi7lh8peHElQ24nVjbzwU+Ujbge0Fnt6sLXKGcaxX34kTKZTJHCV8tXy1f40+qtCKHdhxsIfMhLJ6Fot3reM7ZdUvsxHRwBwwGnary2Dj+krJ87GIkBlDDGwPCqMsaE1G73CIwxOUPb0Zm2YYyJjTHNiLZzukaJtvuKjTHghl8OXHz38O2A5gKc9og8IRUW1x0xckqNMdgxupyjZaKW0vD2uTF1bUNChSvrpgPXnVqcV+FUkcahsJ1wuSbbAva7NTIPX5xbnrsXvG7WbUGce7JcNouVjm3Xjuf/EWq7Wir8RhBmjQ2KE76L+4oF237zqQLnRtzwuawqEToXON0NDB069pPjtQRC1z0Z/EdLiw7ht1wpNeHeW/5NBO5dl8xxfnMhCWoTrWpkInSp7Vyo7UgyyWqYs9ysl+UGlFhwfE5NbbXth/RzzdT2M8GJjTEJQ1Y+CL9dQC8ht5hyhO5o6esjgGY3QSin4AfC8ingqwYSwJ1nxqny17u6nUqZzAe/welRJip5leduL6jrkdehO78q/Jmsvg+/oJhcJadiCP67X6rYk82L8HNlNI3VA+e3BdXQUnEJvdsUd24xZa+c2PUKy92IuU687Dpr0OfgN2r97LF9bgu/7Sm1fh5lQ78Ygq/WL2z1Q9FOq4AmCY18/PV06c7BpdKRBgPb1lVWesGVWzY2z1grofu1fLLZEFcKyWyKphKdfJ1lU9RrBb+BPhbA1d3kNifalgsW4CuP3noma22oLrWatbK96udTOBQM75QZm1I4roUrfB59g8daiMLnAZ/7/KHCnwm8wp8RPLDclxGvIaoZvd6tlu8ex8dgKjRwgX/rJYUvGPlqpr5cX9VU4/ZuMR9xuleTczfs6nYSuO1x3YK1hxAqqXGF3z7l487y+Ix13hM64LQQkkDwhcTSE25NkcHTSkbMgULIEBPUrk79AvqI/OfS3rX1iv8voZ9MU8NvFdCIeJ5xAm9rJ/dzRXJzwe+PhoQO6bcSHcidFFhAUfAS4PdHRIz/jwWLMG434x+y6oqg10v6skuDP6SY/g1x+RkMZScqa5b+pdYCf5P6B+LezEMhy6CEAAAAAElFTkSuQmCC"},"427d":function(t,e,s){"use strict";s.r(e);var o=function(){var t=this,e=t.$createElement,s=t._self._c||e;return s("v-app",{attrs:{id:"main-view"}},[s("core-toolbar"),s("v-content",{style:"padding-left: 0px;"},[s("v-fade-transition",{attrs:{mode:"out-in"}},[s("router-view")],1)],1),t.isTeacherCB||t.isStudentCB?t._e():s("div",{attrs:{id:"message-icon"},on:{click:function(e){return t.doOpenMessage()}}},[s("div",{staticClass:"cursor"},[s("img",{attrs:{src:t.MessageIcon}})])]),t.isTeacherCB||t.isStudentCB?s("Chatroom",{directives:[{name:"show",rawName:"v-show",value:t.chatView,expression:"chatView"}],on:{snackbar:t.doSnackbar}}):t._e(),t.isTeacherCB||t.isStudentCB?s("div",{attrs:{id:"chat-icon"},on:{click:function(e){return t.doOpenChat()}}},[t.chatView?t._e():s("div",{staticClass:"cursor",class:{active:t.doReadStatus}},[s("img",{attrs:{src:t.ChatIcon}})]),t.chatView?s("div",{staticClass:"cursor text-white close"},[s("v-icon",[t._v("mdi-close")])],1):t._e()]):t._e(),t.isTeacherCB||t.isStudentCB?s("div",{staticClass:"chatLog"},t._l(t.chatLog,(function(e,o){return s("p",{key:"l"+o,style:"color:"+e.value},[t._v(" "+t._s(e.text)+" ")])})),0):t._e(),s("core-footer")],1)},a=[],n=(s("8e6e"),s("ac6a"),s("456d"),s("bd86")),A=s("2f62"),i=s("4360"),c=s("2f77"),r=s("2eab"),u=s.n(r),w=s("65c2"),h=s.n(w);function g(t,e){var s=Object.keys(t);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(t);e&&(o=o.filter((function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable}))),s.push.apply(s,o)}return s}function d(t){for(var e=1;e<arguments.length;e++){var s=null!=arguments[e]?arguments[e]:{};e%2?g(Object(s),!0).forEach((function(e){Object(n["a"])(t,e,s[e])})):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(s)):g(Object(s)).forEach((function(e){Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(s,e))}))}return t}var l={name:"MainView",components:{Chatroom:c["default"]},metaInfo:function(){return{title:this.appName}},data:function(){return{MessageIcon:h.a,ChatIcon:u.a,chatView:!1,chatLog:[]}},beforeRouteEnter:function(t,e,s){i["a"].state.fromPath=e.fullPath,i["a"].state.toPath=t.fullPath,s()},computed:d({},Object(A["c"])(["root","appName","fromPath","toPath","isProduction","dologinView","doChatView","doReadStatus"]),{userInfo:function(){return JSON.parse(localStorage.getItem("user"))},isTeacherCB:function(){return!!this.userInfo&&this.userInfo.group.indexOf("test_teacher")>-1},isStudentCB:function(){return!!this.userInfo&&this.userInfo.group.indexOf("test_student")>-1}}),watch:{"$route.fullPath":function(t){this.doGtagsPageview()},doChatView:function(t){this.chatView=t},chatView:function(t){this.$store.state.doChatView=t}},mounted:function(){this.doGtagsPageview()},methods:{doOpenMessage:function(){window.open("https://reurl.cc/XeDE93","_blank")},doGtagsPageview:function(){this.$store.state.root=this.$http.defaults.baseURL,this.$store.state.isProduction="https://www.quikok.com"===this.root,this.isProduction&&this.$gtag.pageview({from_path:this.fromPath,page_path:this.toPath,hostname:this.root,user_id:this.userInfo?this.userInfo.user_id:-1})},doOpenChat:function(){localStorage.getItem("token")?this.chatView=!this.chatView:this.$store.state.dologinView=!0},doSnackbar:function(t){this.chatLog.push({value:t[0],text:t[1]})}}},b=l,C=(s("b32a"),s("2877")),p=Object(C["a"])(b,o,a,!1,null,null,null);e["default"]=p.exports},"65c2":function(t,e){t.exports="data:image/png;base64,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"},b32a:function(t,e,s){"use strict";var o=s("c6b8"),a=s.n(o);a.a},c6b8:function(t,e,s){}}]);
//# sourceMappingURL=chunk-7abbd76e.99800e63.js.map