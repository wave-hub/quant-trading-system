import React, { useState } from 'react';
import { Card, Table, Button, Space, message, Typography, Modal, Badge } from 'antd';
import { SyncOutlined, LineChartOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import ReactECharts from 'echarts-for-react';
import { getStocks, syncStocks, syncMarketData, getMarketData } from '../../services/data';
import type { Stock } from '../../types/data';

const { Title } = Typography;

const DataPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);
  const [isChartVisible, setIsChartVisible] = useState(false);

  const { data: stocksData, isLoading: isLoadingStocks } = useQuery({
    queryKey: ['stocks'],
    queryFn: () => getStocks({ limit: 1000 }),
  });

  const { data: marketData, isLoading: isLoadingMarket } = useQuery({
    queryKey: ['marketData', selectedSymbol],
    queryFn: () => getMarketData({ symbol: selectedSymbol! }),
    enabled: !!selectedSymbol,
  });

  const syncStocksMutation = useMutation({
    mutationFn: syncStocks,
    onSuccess: (res) => {
      message.success(`成功同步 ${res.synced_count} 条股票基本信息数据`);
      queryClient.invalidateQueries({ queryKey: ['stocks'] });
    },
    onError: (err: any) => message.error(err.response?.data?.detail || '同步失败'),
  });

  const syncMarketDataMutation = useMutation({
    mutationFn: syncMarketData,
    onSuccess: (res) => {
      message.success(`成功向上游同步 ${res.synced_count} 条K线数据`);
      queryClient.invalidateQueries({ queryKey: ['marketData', selectedSymbol] });
    },
    onError: (err: any) => message.error(err.response?.data?.detail || '行情同步失败'),
  });

  const openChart = (symbol: string) => {
    setSelectedSymbol(symbol);
    setIsChartVisible(true);
  };

  const columns = [
    { title: '代码', dataIndex: 'symbol', key: 'symbol' },
    { title: '名称', dataIndex: 'name', key: 'name' },
    { 
      title: '市场', 
      dataIndex: 'market', 
      key: 'market',
      render: (market: string) => {
        let color = market === 'SH' ? 'red' : market === 'SZ' ? 'blue' : 'green';
        return <Badge color={color} text={market} />;
      }
    },
    { title: '行业', dataIndex: 'industry', key: 'industry' },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Stock) => (
        <Space size="middle">
          <Button 
            type="link" 
            icon={<SyncOutlined />} 
            loading={syncMarketDataMutation.isPending && selectedSymbol === record.symbol}
            onClick={() => {
              setSelectedSymbol(record.symbol);
              syncMarketDataMutation.mutate({ symbol: record.symbol });
            }}
          >
            同步行情
          </Button>
          <Button type="link" icon={<LineChartOutlined />} onClick={() => openChart(record.symbol)}>
            查看K线
          </Button>
        </Space>
      ),
    },
  ];

  const getChartOptions = () => {
    if (!marketData?.items?.length) return {};
    
    const dates = marketData.items.map(item => item.trade_date);
    const data = marketData.items.map(item => [item.open, item.close, item.low, item.high]);
    const volumes: [string, number, number][] = marketData.items.map(item => [item.trade_date, item.volume, item.open > item.close ? -1 : 1]);
    const ma5Data = marketData.items.map(item => item.ma5 || null);
    const ma20Data = marketData.items.map(item => item.ma20 || null);

    return {
      title: { text: `${selectedSymbol} 日K线图`, left: 0 },
      tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
      legend: { data: ['日K', 'MA5', 'MA20', 'Volume'] },
      grid: [
        { left: '10%', right: '8%', height: '50%' },
        { left: '10%', right: '8%', top: '65%', height: '15%' }
      ],
      xAxis: [
        { type: 'category', data: dates, boundaryGap: false, axisLine: { onZero: false }, splitLine: { show: false } },
        { type: 'category', gridIndex: 1, data: dates, boundaryGap: false, axisLabel: { show: false }, axisTick: { show: false } }
      ],
      yAxis: [
        { scale: true, splitArea: { show: true } },
        { scale: true, gridIndex: 1, splitNumber: 2, axisLabel: { show: false }, axisLine: { show: false }, axisTick: { show: false }, splitLine: { show: false } }
      ],
      dataZoom: [
        { type: 'inside', xAxisIndex: [0, 1], start: 50, end: 100 },
        { show: true, xAxisIndex: [0, 1], type: 'slider', top: '85%', start: 50, end: 100 }
      ],
      series: [
        {
          name: '日K',
          type: 'candlestick',
          data: data,
          itemStyle: { color: '#ef232a', color0: '#14b143', borderColor: '#ef232a', borderColor0: '#14b143' },
        },
        {
          name: 'MA5',
          type: 'line',
          data: ma5Data,
          smooth: true,
          lineStyle: { opacity: 0.8, color: '#f3da21', width: 2 },
          symbol: 'none'
        },
        {
          name: 'MA20',
          type: 'line',
          data: ma20Data,
          smooth: true,
          lineStyle: { opacity: 0.8, color: '#ff28e6', width: 2 },
          symbol: 'none'
        },
        {
          name: 'Volume',
          type: 'bar',
          xAxisIndex: 1,
          yAxisIndex: 1,
          data: volumes.map((item) => ({
            value: item[1],
            itemStyle: { color: item[2] > 0 ? '#ef232a' : '#14b143' }
          }))
        }
      ]
    };
  };

  return (
    <Card 
      title={<Title level={4} style={{ margin: 0 }}>数据管理</Title>} 
      extra={
        <Button 
          type="primary" 
          icon={<SyncOutlined />} 
          loading={syncStocksMutation.isPending}
          onClick={() => syncStocksMutation.mutate()}
        >
          全量同步股票基本信息
        </Button>
      }
    >
      <Table 
        columns={columns} 
        dataSource={stocksData?.items || []} 
        rowKey="symbol" 
        loading={isLoadingStocks}
        pagination={{ pageSize: 10, showSizeChanger: true }}
      />

      <Modal
        title={false}
        open={isChartVisible}
        onCancel={() => setIsChartVisible(false)}
        width={1000}
        footer={null}
        destroyOnClose
      >
        <div style={{ padding: '24px 0 0 0' }}>
          {isLoadingMarket ? (
            <div style={{ textAlign: 'center', padding: '50px 0' }}>加载中...</div>
          ) : !marketData?.items?.length ? (
            <div style={{ textAlign: 'center', padding: '50px 0' }}>暂无数据，请先点击"同步行情"获取数据。</div>
          ) : (
            <ReactECharts option={getChartOptions()} style={{ height: 600 }} />
          )}
        </div>
      </Modal>
    </Card>
  );
};

export default DataPage;
