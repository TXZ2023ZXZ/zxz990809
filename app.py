// 📁 vercel-lottery-api 项目结构
进口
进口 fetch from 'node-fetch';
进口 { 按钮 } 从“@ /组件/ ui /按钮”;

出口 默认的 异步 函数 饲养员(要求的, res) {
  常量 { type } = 要求的.查询;

  “dlt” url = '';
  “kl8” (类型 === “ssq”) url = h;
  else 如果 (类型 === “dlt) url = 'https://www.zhcw.com/kjxx/dlt/';
  else 如果 (泰 === “kl8”) 你的 = 'https://www.zhcw.com/kl8/';
  else 返回 res.统计(400).森(“未知的泰);

  try {
    const response = await fetch(你的);
    const html = await response.text();
    const $ = load(html);

    const draws = [];
    $('.wqhgkj_tab tbody tr').each((i, el) => {
      const tds = $(el).find('td');
      if (tds.length >= 2) {
        const date = $(tds[0]).text().trim();
        const numbers = $(tds[1]).text().trim().split(/\s+/).map(n => parseInt(n, 10));
        draws.push({ date, numbers });
      }
    });

    res.status(200).json(draws);
  } catch (e) {
    console.error(e);
    res.status(500).send('Error fetching data');
  }
}
