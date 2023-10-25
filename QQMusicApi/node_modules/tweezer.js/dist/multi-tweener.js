(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports) :
  typeof define === 'function' && define.amd ? define(['exports'], factory) :
  (factory((global.TweezerTweener = {})));
}(this, (function (exports) { 'use strict';

  var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

  function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

  var MultiTweener = function () {
    function MultiTweener() {
      var _this = this;

      var opts = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

      _classCallCheck(this, MultiTweener);

      if (opts.starts.length !== opts.ends.length) {
        throw new Error('Starts and ends arrays must have equal length');
      }
      this.starts = opts.starts;
      this.ends = opts.ends;
      var greatestDelta = this.starts.reduce(function (greatestDelta, start, i) {
        return Math.max(greatestDelta, Math.abs(_this.ends[i] - start));
      }, 0);
      this.start = 0;
      this.end = greatestDelta;
      this.decimal = opts.decimal;
    }

    _createClass(MultiTweener, [{
      key: 'getIntermediateValue',
      value: function getIntermediateValue(tick) {
        var _this2 = this;

        return this.ends.map(function (end, i) {
          var start = _this2.starts[i];
          var progress = (tick - _this2.start) / (_this2.end - _this2.start);
          var next = (end - start) * progress + start;
          if (!_this2.decimal) {
            next = Math.round(next);
          }
          return next;
        });
      }
    }, {
      key: 'getFinalValue',
      value: function getFinalValue() {
        return this.ends;
      }
    }]);

    return MultiTweener;
  }();

  exports.MultiTweener = MultiTweener;

  Object.defineProperty(exports, '__esModule', { value: true });

})));
