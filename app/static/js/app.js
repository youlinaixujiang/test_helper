/**
 * Neural Terminal — AI 测试 Agent 平台
 * 交互逻辑：标签页、骨架屏、API 调用、Toast、流程串联
 */

(function () {
  'use strict';

  // ---- State ----
  const state = {
    currentTab: 'requirement',
    url: '',
    urlAccessible: false,
    apiHints: [],
    scriptPageUrl: '',
    scriptPageAccessible: false,
    pageText: '',
    pageTitle: '',
    requirement: { input: '', result: null },
    testcase: { input: null, result: null },
    script: { type: 'api', result: null },
    defect: { input: '', result: null },
  };

  // ---- Toast System ----
  const toastQueue = [];
  let toastTimer = null;

  function showToast(msg, type) {
    type = type || 'success';
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    toast.textContent = msg;
    container.appendChild(toast);
    requestAnimationFrame(function () {
      toast.classList.add('show');
    });
    setTimeout(function () {
      toast.classList.remove('show');
      setTimeout(function () { toast.remove(); }, 350);
    }, 3200);
  }

  // ---- Tab Switching ----
  function switchTab(tab) {
    state.currentTab = tab;
    document.querySelectorAll('.tab-btn').forEach(function (btn) {
      btn.classList.remove('active');
    });
    document.querySelectorAll('.panel').forEach(function (panel) {
      panel.classList.remove('active');
    });

    var tabBtn = document.querySelector('[data-tab="' + tab + '"]');
    var panel = document.getElementById('panel-' + tab);
    if (tabBtn) tabBtn.classList.add('active');
    if (panel) panel.classList.add('active');

    updateFlowSteps();
  }

  // ---- Flow Step Indicator ----
  function updateFlowSteps() {
    var steps = document.querySelectorAll('.flow-step');
    var sequence = ['requirement', 'testcase', 'script', 'defect'];
    var currentIdx = sequence.indexOf(state.currentTab);

    steps.forEach(function (step) {
      var stepTab = step.getAttribute('data-step');
      var stepIdx = sequence.indexOf(stepTab);
      step.classList.remove('done', 'active', 'clickable');
      step.querySelector('.flow-num').style.display = 'inline-block';

      if (stepTab === 'requirement' && state.requirement.result) {
        step.classList.add('done', 'clickable');
        step.style.cursor = 'pointer';
      }
      if (stepTab === 'testcase' && state.testcase.result) {
        step.classList.add('done', 'clickable');
        step.style.cursor = 'pointer';
      }
      if (stepTab === 'script' && state.script.result) {
        step.classList.add('done', 'clickable');
        step.style.cursor = 'pointer';
      }
      if (stepTab === 'defect' && state.defect.result) {
        step.classList.add('done', 'clickable');
        step.style.cursor = 'pointer';
      }

      if (stepIdx === currentIdx) {
        step.classList.add('active');
        step.classList.remove('clickable');
        step.style.cursor = 'default';
      }
    });
  }

  document.querySelectorAll('.flow-step').forEach(function (step) {
    step.addEventListener('click', function () {
      if (this.classList.contains('clickable')) {
        switchTab(this.getAttribute('data-step'));
      }
    });
  });

  // ---- Skeleton / Loading ----
  function showSkeleton(panelId) {
    var sk = document.getElementById(panelId + '-skeleton');
    var out = document.getElementById(panelId + '-output');
    if (sk) sk.classList.add('show');
    if (out) out.classList.remove('show');
  }

  function hideSkeleton(panelId) {
    var sk = document.getElementById(panelId + '-skeleton');
    if (sk) sk.classList.remove('show');
  }

  function showOutput(panelId) {
    var out = document.getElementById(panelId + '-output');
    if (out) out.classList.add('show');
  }

  // ---- API Call Helper ----
  function apiCall(url, body, panelId) {
    showSkeleton(panelId);
    var btn = document.getElementById(panelId + '-btn');
    if (btn) btn.disabled = true;

    return fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
      .then(function (resp) {
        return resp.json().then(function (data) {
          if (!resp.ok) throw new Error(data.detail || '请求失败');
          return data;
        });
      })
      .finally(function () {
        hideSkeleton(panelId);
        if (btn) btn.disabled = false;
      });
  }

  // ================================================================
  //  REQUIREMENT AGENT
  // ================================================================

  function onUrlInput() {
    var urlEl = document.getElementById('req-url');
    var btn = document.getElementById('url-check-btn');
    var statusEl = document.getElementById('url-status');
    btn.disabled = !urlEl.value.trim();
    // 重置 URL 状态
    state.url = '';
    state.urlAccessible = false;
    statusEl.innerHTML = '';
    statusEl.className = 'url-status';
  }

  function checkWebsiteUrl() {
    var urlEl = document.getElementById('req-url');
    var url = urlEl.value.trim();
    if (!url) return;

    // 自动补全协议
    if (!/^https?:\/\//i.test(url)) {
      url = 'http://' + url;
      urlEl.value = url;
    }

    var statusEl = document.getElementById('url-status');
    var btn = document.getElementById('url-check-btn');
    statusEl.className = 'url-status checking';
    statusEl.innerHTML = '<span class="dot"></span> 正在检测网站...';
    btn.disabled = true;

    fetch('/api/v1/requirement/check-url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url }),
    })
      .then(function (r) { return r.json(); })
      .then(function (resp) {
        var info = resp.data;
        if (info.accessible) {
          var apiCount = (info.api_hints && info.api_hints.length) ? info.api_hints.length : 0;
          statusEl.className = 'url-status success';
          statusEl.innerHTML = '<span class="dot"></span> 网站可访问 — ' + (info.title || '无标题') + (apiCount ? ' | 发现 ' + apiCount + ' 个 API 端点' : '');
          state.url = url;
          state.urlAccessible = true;
          state.apiHints = info.api_hints || [];
          // 同步更新 JMeter 端点计数
          var hintCountEl = document.getElementById('jmeter-api-hint-count');
          if (hintCountEl) { hintCountEl.textContent = apiCount; }
          showToast('网站检测成功: ' + info.title + (apiCount ? ' (发现 ' + apiCount + ' 个 API)' : ''), 'success');
        } else {
          statusEl.className = 'url-status error';
          statusEl.innerHTML = '<span class="dot"></span> ' + (info.error || '无法访问');
          state.url = '';
          state.urlAccessible = false;
          showToast(info.error || '网站不可访问', 'warning');
        }
      })
      .catch(function (err) {
        statusEl.className = 'url-status error';
        statusEl.innerHTML = '<span class="dot"></span> 检测失败: ' + err.message;
        state.url = '';
        state.urlAccessible = false;
        showToast('网址检测失败', 'error');
      })
      .finally(function () {
        btn.disabled = false;
      });
  }

  function parseRequirement(isFeedback) {
    var content = document.getElementById('req-input').value.trim();
    if (!content && !isFeedback) {
      showToast('请输入测试需求描述', 'error');
      return;
    }

    var body = { content: content || state.requirement.input || '' };
    // 如果检测了 URL 且可访问，传递给后端
    if (state.urlAccessible && state.url) {
      body.url = state.url;
    }
    if (isFeedback) {
      body.feedback = document.getElementById('req-feedback').value.trim();
      if (!body.feedback) { showToast('请输入修改意见', 'error'); return; }
      body.previous_result = state.requirement.result;
    }

    apiCall('/api/v1/requirement/parse', body, 'req')
      .then(function (result) {
        if (!result || !result.data) return;
        state.requirement = { input: content || state.requirement.input, result: result.data };
        // 保存页面文本上下文，供用例生成时使用
        if (result.page_context && result.page_context.content) {
          state.pageText = result.page_context.content;
          state.pageTitle = result.page_context.title || '';
        }
        document.getElementById('req-result').textContent = JSON.stringify(result.data, null, 2);
        showOutput('req');
        document.getElementById('req-feedback-area').classList.add('show');
        updateFlowSteps();
        var msg = '需求解析完成';
        if (state.urlAccessible) msg += ' (基于 ' + state.url + ' 的页面上下文)';
        showToast(msg + ' \u2713');
      })
      .catch(function (err) {
        showToast(err.message, 'error');
      });
  }

  function saveRequirement() {
    if (!state.requirement.result) { showToast('没有可保存的数据', 'error'); return; }
    fetch('/api/v1/requirement/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(state.requirement.result),
    })
      .then(function (r) { return r.json(); })
      .then(function (data) { showToast('已保存: ' + data.filepath); })
      .catch(function (err) { showToast(err.message, 'error'); });
  }

  // ================================================================
  //  TEST CASE AGENT
  // ================================================================
  function generateTestCases(isFeedback) {
    var inputEl = document.getElementById('tc-input');
    var inputText = inputEl.value.trim();

    // 空内容时：自动尝试从需求解析结果填充
    if (!inputText && !isFeedback) {
      if (state.requirement.result) {
        inputEl.value = JSON.stringify(state.requirement.result, null, 2);
        inputText = inputEl.value;
        showToast('已自动填充需求解析结果，即将生成用例...', 'info');
      } else {
        showToast('请先完成「需求解析」或手动输入 JSON', 'error');
        return;
      }
    }

    var requirementResult;
    try {
      requirementResult = isFeedback
        ? state.testcase.input
        : JSON.parse(inputText);
    } catch (e) {
      showToast('JSON 格式错误，请确认输入为有效的 JSON', 'error');
      return;
    }

    var body = { requirement_result: requirementResult };
    if (state.urlAccessible && state.url) {
      body.base_url = state.url;
    }
    // 传递页面文本上下文，消除幻觉
    if (state.pageText) {
      body.page_text = '[页面标题] ' + (state.pageTitle || '') + '\n\n' + state.pageText;
    }
    if (isFeedback) {
      body.feedback = document.getElementById('tc-feedback').value.trim();
      if (!body.feedback) { showToast('请输入修改意见', 'error'); return; }
      body.previous_result = state.testcase.result;
    }

    apiCall('/api/v1/testcase/generate', body, 'tc')
      .then(function (result) {
        if (!result || !result.data) {
          showToast('返回数据为空，请重试', 'error');
          return;
        }
        state.testcase = { input: requirementResult, result: result.data };
        document.getElementById('tc-result').textContent = JSON.stringify(result.data, null, 2);
        showOutput('tc');
        document.getElementById('tc-feedback-area').classList.add('show');
        updateFlowSteps();
        if (!isFeedback) showToast('用例生成完成 ✓，共 ' + (Array.isArray(result.data) ? result.data.length : 'N') + ' 条用例');
        else showToast('已根据反馈更新用例 ✓');
      })
      .catch(function (err) {
        showToast(err.message, 'error');
      });
  }

  function saveTestCases() {
    if (!state.testcase.result) { showToast('没有可保存的数据', 'error'); return; }
    fetch('/api/v1/testcase/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(state.testcase.result),
    })
      .then(function (r) { return r.json(); })
      .then(function (data) { showToast('已保存: ' + data.filepath); })
      .catch(function (err) { showToast(err.message, 'error'); });
  }

  function exportTestCasesExcel() {
    if (!state.testcase.result) { showToast('没有可导出的数据', 'error'); return; }
    var testcases = state.testcase.result;
    fetch('/api/v1/testcase/export-excel', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ testcases: testcases, filename: 'testcases' }),
    })
      .then(function (r) {
        if (!r.ok) throw new Error('导出失败');
        return r.blob();
      })
      .then(function (blob) {
        var url = window.URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = 'testcases.xlsx';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        showToast('Excel 导出成功');
      })
      .catch(function (err) { showToast(err.message, 'error'); });
  }

  // ================================================================
  //  SCRIPT AGENT
  // ================================================================
  function onScriptTypeChange() {
    var scriptType = document.getElementById('script-type').value;
    document.getElementById('api-doc-row').style.display = (scriptType === 'api') ? 'flex' : 'none';
    document.getElementById('ui-url-row').style.display = (scriptType === 'ui') ? 'flex' : 'none';
    document.getElementById('jmeter-api-source-row').style.display = (scriptType === 'jmeter') ? 'flex' : 'none';

    // 用例必填标记：UI 类型必须填用例
    document.getElementById('tc-required-badge').style.display = (scriptType === 'ui') ? 'inline' : 'none';

    // 更新 JMeter 端点数量
    if (scriptType === 'jmeter') {
      document.getElementById('jmeter-api-hint-count').textContent = (state.apiHints || []).length;
    }
  }

  function onJmeterApiSourceChange() {
    var source = document.querySelector('input[name="jmeter-api-source"]:checked').value;
    document.getElementById('script-jmeter-api-doc').style.display = (source === 'doc') ? 'block' : 'none';
  }

  function checkScriptPageUrl() {
    var pageUrl = document.getElementById('script-page-url').value.trim();
    if (!pageUrl) { showToast('请输入页面 URL', 'error'); return; }

    var statusEl = document.getElementById('script-page-status');
    statusEl.className = 'url-status loading';
    statusEl.innerHTML = '<span class="dot"></span> 正在检测...';

    fetch('/api/v1/requirement/check-url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: pageUrl }),
    })
      .then(function (r) { return r.json(); })
      .then(function (resp) {
        var info = resp.data;
        if (info.accessible) {
          statusEl.className = 'url-status success';
          statusEl.innerHTML = '<span class="dot"></span> 页面可访问 — ' + (info.title || 'OK');
          state.scriptPageUrl = pageUrl;
          state.scriptPageAccessible = true;
          showToast('页面检测成功: ' + info.title, 'success');
        } else {
          statusEl.className = 'url-status error';
          statusEl.innerHTML = '<span class="dot"></span> ' + (info.error || '无法访问');
          state.scriptPageAccessible = false;
          showToast(info.error || '页面不可访问', 'warning');
        }
      })
      .catch(function () {
        statusEl.className = 'url-status error';
        statusEl.innerHTML = '<span class="dot"></span> 检测失败';
        state.scriptPageAccessible = false;
      });
  }

  function generateScript() {
    var scriptType = document.getElementById('script-type').value;

    // ---- 类型特定校验 ----
    if (scriptType === 'api') {
      var apiDoc = document.getElementById('script-api-doc').value.trim();
      if (!apiDoc) { showToast('请填写接口文档再生成接口测试脚本', 'error'); return; }
    }
    if (scriptType === 'ui') {
      // UI 脚本：必须有页面 URL 且可访问
      var pageUrl = document.getElementById('script-page-url').value.trim() || state.scriptPageUrl;
      if (!pageUrl) { showToast('请填写并检测页面 URL', 'error'); return; }
      // UI 脚本：必须有测试用例
      var tcText = document.getElementById('script-testcases').value.trim();
      if (!tcText) {
        if (state.testcase.result) {
          document.getElementById('script-testcases').value = JSON.stringify(state.testcase.result, null, 2);
        } else {
          showToast('UI 脚本生成需要测试用例，请先完成「用例生成」或手动输入', 'error'); return;
        }
      }
    }
    if (scriptType === 'jmeter') {
      var source = document.querySelector('input[name="jmeter-api-source"]:checked').value;
      if (source === 'doc') {
        var jmeterApiDoc = document.getElementById('script-jmeter-api-doc').value.trim();
        if (!jmeterApiDoc) { showToast('请粘贴接口文档', 'error'); return; }
      } else {
        if (!state.apiHints || state.apiHints.length === 0) {
          showToast('未发现 API 端点，请先在需求分析页检测网址或选择"手动粘贴接口文档"', 'error'); return;
        }
      }
    }

    // ---- 获取测试用例 ----
    var inputEl = document.getElementById('script-testcases');
    var inputText = inputEl.value.trim();

    if (!inputText) {
      if (state.testcase.result) {
        inputEl.value = JSON.stringify(state.testcase.result, null, 2);
        inputText = inputEl.value;
        showToast('已自动填充测试用例，即将生成脚本...', 'info');
      } else {
        showToast('请先完成「用例生成」或手动输入 JSON', 'error');
        return;
      }
    }

    var testcases;
    try { testcases = JSON.parse(inputText); } catch (e) {
      showToast('JSON 格式错误，请确认输入为有效的 JSON', 'error'); return;
    }

    var baseUrl = document.getElementById('script-base-url').value.trim();
    if (!baseUrl && state.urlAccessible && state.url) {
      baseUrl = state.url;
      document.getElementById('script-base-url').value = baseUrl;
    }
    if (!baseUrl) { baseUrl = 'http://localhost:8080'; }

    // 构建请求体
    var body = {
      script_type: scriptType,
      testcases: testcases,
      base_url: baseUrl,
      page_url: (scriptType === 'ui') ? (pageUrl || baseUrl) : baseUrl,
      api_hints: state.apiHints || [],
    };

    // API 类型：传入接口文档
    if (scriptType === 'api') {
      body.api_doc = document.getElementById('script-api-doc').value.trim();
    }

    // JMeter 类型：若选择了文档来源，传入文档
    if (scriptType === 'jmeter') {
      var jSource = document.querySelector('input[name="jmeter-api-source"]:checked').value;
      if (jSource === 'doc') {
        body.api_doc = document.getElementById('script-jmeter-api-doc').value.trim();
      }
    }

    apiCall('/api/v1/script/generate', body, 'script')
      .then(function (result) {
        if (!result || !result.data) return;
        state.script = { type: scriptType, result: result.data };
        document.getElementById('script-result').textContent = result.data.code;
        showOutput('script');

        if (scriptType === 'jmeter') {
          var runnerDiv = document.getElementById('jmx-runner');
          document.getElementById('jmx-runner-btns').style.display = 'flex';
          document.getElementById('jmx-runner-status').classList.remove('show');
          document.getElementById('jmx-runner-result').classList.remove('show');
          document.getElementById('jmx-runner-result').innerHTML = '';
          runnerDiv.classList.add('show');
        } else {
          document.getElementById('jmx-runner').classList.remove('show');
        }
        updateFlowSteps();
        showToast('脚本生成完成 ✓');
      })
      .catch(function (err) {
        showToast(err.message, 'error');
      });
  }

  function saveScript() {
    if (!state.script.result) { showToast('没有可保存的脚本', 'error'); return; }
    fetch('/api/v1/script/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code: state.script.result.code,
        script_type: state.script.type,
        filename: state.script.result.filename,
      }),
    })
      .then(function (r) { return r.json(); })
      .then(function (data) { showToast('已保存: ' + data.filepath); })
      .catch(function (err) { showToast(err.message, 'error'); });
  }

  function runJmeter() {
    var result = state.script.result;
    if (!result || !result.filepath) {
      showToast('请先生成 JMX 脚本', 'error');
      return;
    }

    var fname = result.filepath || result.filename;
    var runnerDiv = document.getElementById('jmx-runner');
    var btnsDiv = document.getElementById('jmx-runner-btns');
    var statusDiv = document.getElementById('jmx-runner-status');
    var resultDiv = document.getElementById('jmx-runner-result');

    // 显示执行状态
    btnsDiv.style.display = 'none';
    statusDiv.classList.add('show');
    resultDiv.classList.remove('show');
    resultDiv.innerHTML = '';

    fetch('/api/v1/script/run-jmeter', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ jmx_filepath: fname, base_url: state.url || 'http://localhost:8080' }),
    })
      .then(function (r) { return r.json(); })
      .then(function (resp) {
        statusDiv.classList.remove('show');

        if (!resp.success) {
          showToast(resp.detail || 'JMeter 执行失败', 'error');
          resultDiv.innerHTML = '<div class="stat-line stat-fail">' + (resp.detail || '未知错误') + '</div>';
          resultDiv.classList.add('show');
          btnsDiv.style.display = 'flex';
          return;
        }

        var data = resp.data;
        var summary = data.summary || {};

        // 构建结果展示
        var html = '<div class="stat-line">JMeter 执行完成 (退出码: ' + (data.exit_code || 0) + ')</div>';
        html += '<div class="stat-line" style="margin-top:8px;">';
        html += '总请求: <strong>' + (summary.total || 0) + '</strong> | ';
        html += '通过: <strong class="stat-pass">' + (summary.passed || 0) + '</strong> | ';
        html += '失败: <strong class="stat-fail">' + (summary.failed || 0) + '</strong> | ';
        html += '错误率: <strong>' + (summary.error_rate || '0%') + '</strong>';
        html += '</div>';
        html += '<div class="stat-line">';
        html += '平均耗时: <strong>' + (summary.avg_time_ms || 0) + 'ms</strong> | ';
        html += '最小/最大: ' + (summary.min_time_ms || 0) + 'ms / ' + (summary.max_time_ms || 0) + 'ms';
        html += '</div>';

        // 如果有按接口分组统计
        var byLabel = summary.by_label || {};
        var labelKeys = Object.keys(byLabel);
        if (labelKeys.length > 0) {
          html += '<div class="stat-line" style="margin-top:8px;">';
          html += '<span class="stat-label">按接口统计:</span>';
          html += '</div>';
          labelKeys.forEach(function (lbl) {
            var item = byLabel[lbl];
            var cls = item.failed > 0 ? 'stat-fail' : 'stat-pass';
            html += '<div class="stat-line" style="padding-left:12px;">';
            html += '' + lbl + ': ';
            html += '<span class="' + cls + '">' + item.passed + '/' + item.total + '</span>';
            html += '</div>';
          });
        }

        resultDiv.innerHTML = html;
        resultDiv.classList.add('show');

        // 构建缺陷分析所需的文本
        var defectText = _buildDefectText(data);

        // 自动填入缺陷分析输入框
        var defectInput = document.getElementById('defect-input');
        if (defectInput) {
          defectInput.value = defectText;
          state.defect.input = defectText;
        }

        showToast('JMeter 测试完成 ✓ 结果已发送到缺陷分析模块', 'success');

        // 延迟切换到缺陷分析 Tab
        setTimeout(function () {
          switchTab('defect');
        }, 800);
      })
      .catch(function (err) {
        statusDiv.classList.remove('show');
        showToast('执行出错: ' + err.message, 'error');
        resultDiv.innerHTML = '<div class="stat-line stat-fail">' + err.message + '</div>';
        resultDiv.classList.add('show');
        btnsDiv.style.display = 'flex';
      });
  }

  function _buildDefectText(data) {
    var lines = [];
    lines.push('=== JMeter 性能测试结果 ===');
    lines.push('');

    var summary = data.summary || {};
    lines.push('[汇总]');
    lines.push('  总请求数: ' + (summary.total || 0));
    lines.push('  通过: ' + (summary.passed || 0));
    lines.push('  失败: ' + (summary.failed || 0));
    lines.push('  错误率: ' + (summary.error_rate || '0%'));
    lines.push('  平均耗时: ' + (summary.avg_time_ms || 0) + 'ms');
    lines.push('  最大耗时: ' + (summary.max_time_ms || 0) + 'ms');
    lines.push('  最小耗时: ' + (summary.min_time_ms || 0) + 'ms');
    lines.push('');

    var samples = data.samples || [];
    if (samples.length > 0) {
      lines.push('[接口请求明细]');
      samples.forEach(function (s) {
        var status = s.success ? 'PASS' : 'FAIL';
        var line = '  ' + status + ' | ' + s.label + ' | ' + s.response_code + ' | ' + s.elapsed_ms + 'ms';
        if (!s.success) {
          line += ' | 错误: ' + (s.response_message || '');
        }
        lines.push(line);
      });
      lines.push('');
    }

    // 添加失败样本详情
    var failures = samples.filter(function (s) { return !s.success; });
    if (failures.length > 0) {
      lines.push('[失败请求详情]');
      failures.forEach(function (s) {
        lines.push('  接口: ' + s.label);
        lines.push('  响应码: ' + s.response_code);
        lines.push('  错误信息: ' + (s.response_message || '无'));
        lines.push('  耗时: ' + s.elapsed_ms + 'ms');
        lines.push('');
      });
    }

    lines.push('请分析以上性能测试结果中的缺陷和异常。');
    return lines.join('\n');
  }

  // ================================================================
  //  DEFECT AGENT
  // ================================================================
  function analyzeDefects(isFeedback) {
    var testResults = document.getElementById('defect-input').value.trim();
    if (!testResults && !isFeedback) {
      showToast('请输入测试执行结果', 'error');
      return;
    }

    var body = { test_results: testResults || state.defect.input || '' };
    if (isFeedback) {
      body.feedback = document.getElementById('defect-feedback').value.trim();
      if (!body.feedback) { showToast('请输入修改意见', 'error'); return; }
      body.previous_result = state.defect.result;
    }

    apiCall('/api/v1/defect/analyze', body, 'defect')
      .then(function (result) {
        if (!result || !result.data) return;
        state.defect = { input: testResults || state.defect.input, result: result.data };
        document.getElementById('defect-result').textContent = JSON.stringify(result.data, null, 2);
        showOutput('defect');
        document.getElementById('defect-feedback-area').classList.add('show');
        updateFlowSteps();
        if (!isFeedback) showToast('缺陷分析完成 ✓');
        else showToast('已根据反馈更新分析报告 ✓');
      })
      .catch(function (err) {
        showToast(err.message, 'error');
      });
  }

  function saveDefectReport() {
    if (!state.defect.result) { showToast('没有可保存的数据', 'error'); return; }
    fetch('/api/v1/defect/save-report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(state.defect.result),
    })
      .then(function (r) { return r.json(); })
      .then(function (data) { showToast('已保存: ' + data.filepath); })
      .catch(function (err) { showToast(err.message, 'error'); });
  }

  // ================================================================
  //  QUICK-FILL: 从需求结果填充到用例面板
  // ================================================================
  function fillFromRequirement() {
    if (!state.requirement.result) {
      showToast('请先在「需求解析」中完成解析', 'error');
      return;
    }
    document.getElementById('tc-input').value = JSON.stringify(state.requirement.result, null, 2);
    switchTab('testcase');
    showToast('已填充需求解析结果到用例面板', 'info');
  }

  function fillFromTestCases() {
    if (!state.testcase.result) {
      showToast('请先在「用例生成」中生成用例', 'error');
      return;
    }
    document.getElementById('script-testcases').value = JSON.stringify(state.testcase.result, null, 2);
    switchTab('script');
    showToast('已填充用例到脚本生成面板', 'info');
  }

  // ================================================================
  //  DOCUMENT UPLOAD
  // ================================================================
  function handleFileSelect(event) {
    var file = event.target.files[0];
    if (file) uploadDocument(file);
  }

  function uploadDocument(file) {
    var contentEl = document.getElementById('req-upload-content');
    var progressEl = document.getElementById('req-upload-progress');
    var doneEl = document.getElementById('req-upload-done');
    var zone = document.getElementById('req-upload-zone');

    contentEl.style.display = 'none';
    progressEl.classList.add('show');
    doneEl.classList.remove('show');

    var formData = new FormData();
    formData.append('file', file);

    fetch('/api/v1/requirement/upload-document', {
      method: 'POST',
      body: formData,
    })
      .then(function (resp) { return resp.json(); })
      .then(function (data) {
        progressEl.classList.remove('show');
        if (!data.success) {
          contentEl.style.display = '';
          showToast(data.detail || '解析失败', 'error');
          return;
        }
        doneEl.querySelector('.upload-filename').textContent = data.data.filename + ' (' + data.data.size_mb + ' MB)';
        doneEl.classList.add('show');
        document.getElementById('req-input').value = data.data.content;
        showToast('文档解析完成，共 ' + data.data.char_count + ' 字符');
      })
      .catch(function (err) {
        progressEl.classList.remove('show');
        contentEl.style.display = '';
        showToast('上传失败: ' + err.message, 'error');
      });

    // reset file input
    document.getElementById('req-file-input').value = '';
  }

  function clearDocument() {
    var contentEl = document.getElementById('req-upload-content');
    var doneEl = document.getElementById('req-upload-done');
    var progressEl = document.getElementById('req-upload-progress');

    contentEl.style.display = '';
    doneEl.classList.remove('show');
    progressEl.classList.remove('show');
    document.getElementById('req-input').value = '';
    document.getElementById('req-file-input').value = '';
  }

  function initUploadZone() {
    var zone = document.getElementById('req-upload-zone');
    var fileInput = document.getElementById('req-file-input');

    // Click to select file
    zone.addEventListener('click', function (e) {
      if (e.target.closest('.btn-clear')) return;
      fileInput.click();
    });

    // Drag & drop
    zone.addEventListener('dragover', function (e) {
      e.preventDefault();
      zone.classList.add('drag-over');
    });
    zone.addEventListener('dragleave', function () {
      zone.classList.remove('drag-over');
    });
    zone.addEventListener('drop', function (e) {
      e.preventDefault();
      zone.classList.remove('drag-over');
      var file = e.dataTransfer.files[0];
      if (file) uploadDocument(file);
    });
  }

  // ---- Global Exports ----
  window.switchTab = switchTab;
  window.parseRequirement = parseRequirement;
  window.saveRequirement = saveRequirement;
  window.onUrlInput = onUrlInput;
  window.checkWebsiteUrl = checkWebsiteUrl;
  window.generateTestCases = generateTestCases;
  window.saveTestCases = saveTestCases;
  window.exportTestCasesExcel = exportTestCasesExcel;
  window.generateScript = generateScript;
  window.onScriptTypeChange = onScriptTypeChange;
  window.onJmeterApiSourceChange = onJmeterApiSourceChange;
  window.checkScriptPageUrl = checkScriptPageUrl;
  window.saveScript = saveScript;
  window.runJmeter = runJmeter;
  window.analyzeDefects = analyzeDefects;
  window.saveDefectReport = saveDefectReport;
  window.fillFromRequirement = fillFromRequirement;
  window.fillFromTestCases = fillFromTestCases;
  window.handleFileSelect = handleFileSelect;
  window.clearDocument = clearDocument;
  window.uploadDocument = uploadDocument;

  // ---- Init ----
  updateFlowSteps();
  initUploadZone();
  onScriptTypeChange();
})();
