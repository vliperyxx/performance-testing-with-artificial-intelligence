TOOL_RULES = {
    "locust": {
        "required": ["HttpUser", "@task", "self.client"],
        "forbidden": ["runner.start(", "events.test_start", "os.system(", "__main__", "FastHttpUser", "host =", "LoadTestShape"],
        "notes": (
            "Do not set host inside the class because the host is provided by the runner. "
            "Use wait_time = between(1, 2) to simulate realistic user think time. "
            "Use catch_response=True and response.failure() to validate response status code. "
        )
    },

    "k6": {
        "required": ["import http from 'k6/http'", "export const options", "export default function"],
        "forbidden": ["setTimeout(", "while (true)", "require(", "fs.", "process.", "k6/experimental"],
        "notes": (
            "Use check() to validate response status code. "
            "Never use both duration and stages in options at the same time. Use either duration or stages. "
            "Use sleep(1) at the end of the default function to simulate realistic user think time. "
        )
    },

    "jmeter": {
        "required": ["<jmeterTestPlan", "<ThreadGroup", "<HTTPSamplerProxy"],
        "forbidden": ["DebugSampler", "ViewResultsTree"],
        "notes": (
            "Use ThreadGroup with num_threads, ramp_time, scheduler=true, duration, and loops=-1 for sustained tests. "
            "Never put the full URL into HTTPSampler.path. "
            "Always use protocol=http, domain=localhost, port=3000, and path only as /endpoint. "
            "Use Response Assertion to validate response status code. "
            "Add a small ConstantTimer delay, for example 300 ms, to avoid unrealistically aggressive local load. "
        )
    },

    "gatling": {
        "required": ["Simulation", "scenario(", ".exec(", "http(", "io.gatling.javaapi.core", "io.gatling.javaapi.http"],
        "forbidden": ["println(", "Thread.sleep(", "Iterator.continually(", "scala."],
        "notes": (
            "Use Gatling Java DSL, not Scala. "
            "Use check(status().is(...)) to validate response status code. "
            "Use setUp() with injectClosed() for virtual user based load. "
            "Interpret the Virtual users parameter as concurrent users, not users per second. "
            "For sustained load, use rampConcurrentUsers(0).to(VIRTUAL_USERS).during(RAMP_UP) and constantConcurrentUsers(VIRTUAL_USERS).during(DURATION). "
            "Do not use rampUsers alone for sustained tests because it creates a single-pass load. "
            "For dynamic feeders in Java DSL, use Stream.generate(...).iterator(). "
            "Use pause() between requests to simulate realistic user think time, for example .pause(Duration.ofSeconds(1))"
        )
    }
}

LOCUST_EXAMPLE = """from locust import HttpUser, task, between

class LoadUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def test_login(self):
        with self.client.post(
            "/users/login",
            json={"email": "o.melnychuk@gmail.com", "password": "qN4#Lv7tBxR9"},
            headers={"Content-Type": "application/json"},
            catch_response=True,
            timeout=10
        ) as response:
            if response.status_code != 201:
                response.failure(f"Unexpected status code: {response.status_code}")
"""

K6_EXAMPLE = """import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    vus: 2,
    duration: '15s',
};

export default function () {
    const payload = JSON.stringify({
        email: 'o.melnychuk@gmail.com',
        password: 'qN4#Lv7tBxR9',
    });

    const params = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    const res = http.post('http://localhost:3000/users/login', payload, params);

    check(res, {
        'status is 201': (r) => r.status === 201,
    });
    sleep(1); 
}
"""

JMETER_EXAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Login Test">
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments"/>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Users">
        <intProp name="ThreadGroup.num_threads">2</intProp>
        <intProp name="ThreadGroup.ramp_time">2</intProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
        <stringProp name="ThreadGroup.duration">15</stringProp>
        <boolProp name="ThreadGroup.scheduler">true</boolProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController">
          <stringProp name="LoopController.loops">-1</stringProp>
          <boolProp name="LoopController.continue_forever">false</boolProp>
        </elementProp>
      </ThreadGroup>
      <hashTree>
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="Login">
          <stringProp name="HTTPSampler.domain">localhost</stringProp>
          <stringProp name="HTTPSampler.port">3000</stringProp>
          <stringProp name="HTTPSampler.protocol">http</stringProp>
          <stringProp name="HTTPSampler.path">/users/login</stringProp>
          <stringProp name="HTTPSampler.method">POST</stringProp>
          <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
            <collectionProp name="Arguments.arguments">
              <elementProp name="" elementType="HTTPArgument">
                <boolProp name="HTTPArgument.always_encode">false</boolProp>
                <stringProp name="Argument.value">{"email":"o.melnychuk@gmail.com","password":"qN4#Lv7tBxR9"}</stringProp>
                <stringProp name="Argument.metadata">=</stringProp>
              </elementProp>
            </collectionProp>
          </elementProp>
        </HTTPSamplerProxy>
        <hashTree>
          <HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="Headers">
            <collectionProp name="HeaderManager.headers">
              <elementProp name="" elementType="Header">
                <stringProp name="Header.name">Content-Type</stringProp>
                <stringProp name="Header.value">application/json</stringProp>
              </elementProp>
            </collectionProp>
          </HeaderManager>
          <hashTree/>

          <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Status 201">
            <collectionProp name="Asserion.test_strings">
              <stringProp name="49587">201</stringProp>
            </collectionProp>
            <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
            <boolProp name="Assertion.assume_success">false</boolProp>
            <intProp name="Assertion.test_type">8</intProp>
          </ResponseAssertion>
          <hashTree/>

          <ConstantTimer guiclass="ConstantTimerGui" testclass="ConstantTimer" testname="Think Time">
            <stringProp name="ConstantTimer.delay">300</stringProp>
          </ConstantTimer>
          <hashTree/>
        </hashTree>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
"""

GATLING_EXAMPLE = """import io.gatling.javaapi.core.*;
import io.gatling.javaapi.http.*;
import static io.gatling.javaapi.core.CoreDsl.*;
import static io.gatling.javaapi.http.HttpDsl.*;
import java.time.Duration;

public class LoginSimulation extends Simulation {

    HttpProtocolBuilder httpProtocol = http
        .baseUrl("http://localhost:3000")
        .acceptHeader("application/json")
        .contentTypeHeader("application/json");

    ScenarioBuilder scn = scenario("Login")
        .exec(
            http("POST Login")
                .post("/users/login")
                .body(StringBody("{\\"email\\":\\"o.melnychuk@gmail.com\\",\\"password\\":\\"qN4#Lv7tBxR9\\"}"))
                .check(status().is(201))
        );

    {
        setUp(
            scn.injectClosed(
                rampConcurrentUsers(0).to(2).during(Duration.ofSeconds(2)),
                constantConcurrentUsers(2).during(Duration.ofSeconds(15))
            )
        ).protocols(httpProtocol);
    }
}
"""

TOOL_EXAMPLES = {"locust": LOCUST_EXAMPLE, "k6": K6_EXAMPLE, "jmeter": JMETER_EXAMPLE, "gatling": GATLING_EXAMPLE}