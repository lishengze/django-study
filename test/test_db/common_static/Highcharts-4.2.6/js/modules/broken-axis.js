(function(f){typeof module==="object"&&module.exports?module.exports=f:f(Highcharts)})(function(f){function t(){return Array.prototype.slice.call(arguments,1)}function r(g){g.apply(this);this.drawBreaks(this.xAxis,["x"]);this.drawBreaks(this.yAxis,p(this.pointArrayMap,["y"]))}var p=f.pick,n=f.wrap,q=f.each,u=f.extend,s=f.fireEvent,o=f.Axis,v=f.Series;u(o.prototype,{isInBreak:function(g,e){var b=g.repeat||Infinity,c=g.from,a=g.to-g.from,b=e>=c?(e-c)%b:b-(c-e)%b;return g.inclusive?b<=a:b<a&&b!==0},
isInAnyBreak:function(g,e){var b=this.options.breaks,c=b&&b.length,a,d,k;if(c){for(;c--;)this.isInBreak(b[c],g)&&(a=!0,d||(d=p(b[c].showPoints,this.isXAxis?!1:!0)));k=a&&e?a&&!d:a}return k}});n(o.prototype,"setTickPositions",function(g){g.apply(this,Array.prototype.slice.call(arguments,1));if(this.options.breaks){var e=this.tickPositions,b=this.tickPositions.info,c=[],a;for(a=0;a<e.length;a++)this.isInAnyBreak(e[a])||c.push(e[a]);this.tickPositions=c;this.tickPositions.info=b}});n(o.prototype,"init",
function(g,e,b){if(b.breaks&&b.breaks.length)b.ordinal=!1;g.call(this,e,b);if(this.options.breaks){var c=this;c.isBroken=!0;this.val2lin=function(a){var d=a,k,b;for(b=0;b<c.breakArray.length;b++)if(k=c.breakArray[b],k.to<=a)d-=k.len;else if(k.from>=a)break;else if(c.isInBreak(k,a)){d-=a-k.from;break}return d};this.lin2val=function(a){var d,b;for(b=0;b<c.breakArray.length;b++)if(d=c.breakArray[b],d.from>=a)break;else d.to<a?a+=d.len:c.isInBreak(d,a)&&(a+=d.len);return a};this.setExtremes=function(a,
d,c,b,g){for(;this.isInAnyBreak(a);)a-=this.closestPointRange;for(;this.isInAnyBreak(d);)d-=this.closestPointRange;o.prototype.setExtremes.call(this,a,d,c,b,g)};this.setAxisTranslation=function(a){o.prototype.setAxisTranslation.call(this,a);var d=c.options.breaks,a=[],b=[],g=0,e,h,l=c.userMin||c.min,f=c.userMax||c.max,i,m;for(m in d)h=d[m],e=h.repeat||Infinity,c.isInBreak(h,l)&&(l+=h.to%e-l%e),c.isInBreak(h,f)&&(f-=f%e-h.from%e);for(m in d){h=d[m];i=h.from;for(e=h.repeat||Infinity;i-e>l;)i-=e;for(;i<
l;)i+=e;for(;i<f;i+=e)a.push({value:i,move:"in"}),a.push({value:i+(h.to-h.from),move:"out",size:h.breakSize})}a.sort(function(a,b){return a.value===b.value?(a.move==="in"?0:1)-(b.move==="in"?0:1):a.value-b.value});d=0;i=l;for(m in a){h=a[m];d+=h.move==="in"?1:-1;if(d===1&&h.move==="in")i=h.value;d===0&&(b.push({from:i,to:h.value,len:h.value-i-(h.size||0)}),g+=h.value-i-(h.size||0))}c.breakArray=b;s(c,"afterBreaks");c.transA*=(f-c.min)/(f-l-g);c.min=l;c.max=f}}});n(v.prototype,"generatePoints",function(g){g.apply(this,
t(arguments));var e=this.xAxis,b=this.yAxis,c=this.points,a,d=c.length,f=this.options.connectNulls,j;if(e&&b&&(e.options.breaks||b.options.breaks))for(;d--;)if(a=c[d],j=a.y===null&&f===!1,!j&&(e.isInAnyBreak(a.x,!0)||b.isInAnyBreak(a.y,!0)))c.splice(d,1),this.data[d]&&this.data[d].destroyElements()});f.Series.prototype.drawBreaks=function(g,e){var b=this,c=b.points,a,d,f,j;q(e,function(e){a=g.breakArray||[];d=g.isXAxis?g.min:p(b.options.threshold,g.min);q(c,function(b){j=p(b["stack"+e.toUpperCase()],
b[e]);q(a,function(a){f=!1;if(d<a.from&&j>a.to||d>a.from&&j<a.from)f="pointBreak";else if(d<a.from&&j>a.from&&j<a.to||d>a.from&&j>a.to&&j<a.from)f="pointInBreak";f&&s(g,f,{point:b,brk:a})})})})};n(f.seriesTypes.column.prototype,"drawPoints",r);n(f.Series.prototype,"drawPoints",r)});