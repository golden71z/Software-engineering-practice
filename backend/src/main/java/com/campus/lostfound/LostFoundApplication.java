package com.campus.lostfound;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 校园失物招领管理系统 - 启动类
 */
@SpringBootApplication
@MapperScan("com.campus.lostfound.mapper")
public class LostFoundApplication {

    public static void main(String[] args) {
        SpringApplication.run(LostFoundApplication.class, args);
        System.out.println("""

                ==================================================
                  校园失物招领管理系统 - 后端服务启动成功
                  接口地址: http://localhost:8080/api
                  健康检查: http://localhost:8080/api/health
                ==================================================
                """);
    }
}
