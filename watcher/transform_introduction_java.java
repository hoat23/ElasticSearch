import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

public class MyClass {
    public static void main(String args[]) {
      System.out.println("[INI] Iniciando programa...");
      System.out.println("[.01] Printing a map pipeline...");
      List<Integer> bucket_01 = Arrays.asList(3,6,9,12,15);
      bucket_01.stream().map(number -> number*3).forEach(System.out::println);
      
      System.out.println( (  bucket_01.stream().map(number -> number*3) ).getClass().getName()  );
      System.out.println("[.02] Converting a pipeline to list<Integer> and printing...");
      List<Integer> bucket_02 =  bucket_01.stream().map(number -> number*3).collect(Collectors.toList());
      System.out.println( bucket_02 );
      
      System.out.println("[.03] Filtering data..." );
      List<Integer> bucket_03 = bucket_01.stream().filter( n -> {System.out.println("\tfilter : " + n + "\t["+(n%2==0)+"]"); return n%2==0;} ).collect(Collectors.toList());
      System.out.println( "bucket_03 : " + bucket_03 );
      
      System.out.println("[.04] Sum data using stream pipeline" );
      int sum = bucket_01.stream().reduce(0, (a,b) -> a+b);
      System.out.println("\tsum="+sum);
      
      System.out.println("[FIN]");
      
    }
}
