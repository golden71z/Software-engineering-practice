package com.campus.lostfound.controller;

import com.campus.lostfound.common.result.Result;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;

/**
 * 健康检查接口
 * <p>
 * 用于验证前后端联通性，是骨架阶段的核心验证点。
 */
@Slf4j
@RestController
@RequestMapping("/api")
public class HealthController {

    @GetMapping("/health")
    public Result<Map<String, Object>> health() {
        log.info("健康检查请求");

        Map<String, Object> data = new HashMap<>();
        data.put("status", "UP");
        data.put("service", "校园失物招领管理系统");
        data.put("version", "0.0.1-SNAPSHOT");
        data.put("time", LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));

        return Result.success("后端连接成功", data);
    }
}
